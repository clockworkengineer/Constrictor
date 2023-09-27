"""TEST"""

import time
import pathlib
import pytest


from tests.common import (
    create_test_file,
    create_copyfile_config,
    remove_source_destination,
)
from core.constants import (
    CONFIG_SOURCE,
    CONFIG_DESTINATION,
    CONFIG_DELETESOURCE,
    CONFIG_RECURSIVE,
)
from core.config import ConfigDict
from core.watcher import Watcher, WatcherError
from core.factory import Factory
from builtin.copyfile_handler import CopyFileHandler
from builtin.ftp_copyfile_handler import FTPCopyFileHandler


@pytest.fixture(name="generate_config")
def fixture_generate_config() -> ConfigDict:
    Factory.clear()
    Factory.register("CopyFile", CopyFileHandler)
    Factory.register("FTPCopyFile", FTPCopyFileHandler)

    watcher_config: ConfigDict = create_copyfile_config()

    yield watcher_config

    remove_source_destination(watcher_config)


class TestCoreWatcher:
    def __wait_for_processed_files(self, watcher: Watcher, count: int) -> None:
        while watcher.files_processed < count:
            time.sleep(0.01)

    def __copy_count_files(self, watcher_config: ConfigDict, count) -> None:
        watcher = Watcher(watcher_config)
        watcher.start()
        source_path = pathlib.Path(watcher_config[CONFIG_SOURCE])
        destination_path = pathlib.Path(watcher_config[CONFIG_DESTINATION])
        for file_number in range(count):
            create_test_file(source_path / f"test{file_number}.txt")
        self.__wait_for_processed_files(watcher, count)
        for file_number in range(count):
            assert (destination_path / f"test{file_number}.txt").exists() is True
        watcher.stop()

    def test_watcher_with_config_of_none(self) -> None:
        with pytest.raises(WatcherError):
            _ = Watcher(None)  # type: ignore

    def test_watcher_invalid_config(self, generate_config: ConfigDict) -> None:
        generate_config.pop(CONFIG_DESTINATION)
        with pytest.raises(WatcherError):
            _ = Watcher(generate_config)

    def test_watcher_with_a_valid_config(self, generate_config: ConfigDict) -> None:
        watcher = Watcher(generate_config)
        assert watcher is not None

    def test_watcher_with_a_valid_config_check_source_directory(
        self, generate_config: ConfigDict
    ) -> None:
        assert pathlib.Path(generate_config[CONFIG_SOURCE]).exists() is False
        _ = Watcher(generate_config)
        assert pathlib.Path(generate_config[CONFIG_SOURCE]).exists() is True

    def test_watcher_with_a_valid_config_check_desination_directory(
        self, generate_config: ConfigDict
    ) -> None:
        assert pathlib.Path(generate_config[CONFIG_DESTINATION]).exists() is False
        _ = Watcher(generate_config)
        assert pathlib.Path(generate_config[CONFIG_DESTINATION]).exists() is True

    def test_watcher_initial_state_stopped(self, generate_config: ConfigDict) -> None:
        watcher = Watcher(generate_config)
        assert watcher.is_running is False

    def test_watcher_started(self, generate_config: ConfigDict):
        watcher = Watcher(generate_config)
        watcher.start()
        assert watcher.is_running is True

    def test_watcher_start_a_running_watcher(self, generate_config: ConfigDict) -> None:
        watcher = Watcher(generate_config)
        watcher.start()
        watcher.start()
        assert watcher.is_running is True

    def test_watcher_stopping_a_stopped_watcher(
        self, generate_config: ConfigDict
    ) -> None:
        watcher = Watcher(generate_config)
        watcher.start()
        watcher.stop()
        watcher.stop()
        assert watcher.is_running is False

    def test_watcher_started_then_stopped(self, generate_config: ConfigDict) -> None:
        watcher = Watcher(generate_config)
        watcher.start()
        time.sleep(1)
        watcher.stop()
        assert watcher.is_running is False

    def test_watcher_started_then_stopped_then_restarted(
        self, generate_config: ConfigDict
    ) -> None:
        watcher = Watcher(generate_config)
        watcher.start()
        time.sleep(1)
        watcher.stop()
        watcher.start()
        assert watcher.is_running is True

    def test_watcher_copy_a_single_file_from_source_to_destination(
        self, generate_config: ConfigDict
    ) -> None:
        self.__copy_count_files(generate_config, 1)
        assert (
            pathlib.Path(generate_config[CONFIG_SOURCE]) / "test0.txt"
        ).exists() is False

    def test_watcher_copy_a_single_file_from_source_to_destination_keepsource(
        self, generate_config: ConfigDict
    ) -> None:
        generate_config[CONFIG_DELETESOURCE] = False
        self.__copy_count_files(generate_config, 1)
        assert (
            pathlib.Path(generate_config[CONFIG_SOURCE]) / "test0.txt"
        ).exists() is True

    def test_watcher_copy_ten_files_from_source_to_destination(
        self, generate_config: ConfigDict
    ) -> None:
        self.__copy_count_files(generate_config, 10)

    def test_watcher_copy_fifty_files_from_source_to_destination(
        self, generate_config: ConfigDict
    ) -> None:
        self.__copy_count_files(generate_config, 50)

    def test_watcher_copy_onehundred_files_from_source_to_destination(
        self, generate_config: ConfigDict
    ) -> None:
        self.__copy_count_files(generate_config, 100)

    def test_watcher_copy_onethousand_files_from_source_to_destination(
        self, generate_config: ConfigDict
    ) -> None:
        self.__copy_count_files(generate_config, 1000)

    def test_watcher_copy_one_file_recursive_depth_one_deletesource(
        self, generate_config: ConfigDict
    ) -> None:
        generate_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(generate_config)
        watcher.start()
        source_path = pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "test.txt"
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 1)
        watcher.stop()
        assert source_path.exists() is False
        assert (
            pathlib.Path(generate_config[CONFIG_DESTINATION]) / "dir1" / "test.txt"
        ).exists() is True
        assert watcher.files_processed == 1

    def test_watcher_copy_one_file_recursive_depth_two_deletesource(
        self, generate_config: ConfigDict
    ) -> None:
        generate_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(generate_config)
        watcher.start()
        source_path = (
            pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "dir2" / "test.txt"
        )
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 1)
        watcher.stop()
        assert source_path.exists() is False
        assert (
            pathlib.Path(generate_config[CONFIG_DESTINATION])
            / "dir1"
            / "dir2"
            / "test.txt"
        ).exists() is True
        assert watcher.files_processed == 1

    def test_watcher_copy_two_files_recursive_depth_one_deletesource(
        self, generate_config: ConfigDict
    ) -> None:
        generate_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(generate_config)
        watcher.start()
        source_path0 = (
            pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "test00.txt"
        )
        create_test_file(source_path0)
        source_path1 = (
            pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "test01.txt"
        )
        create_test_file(source_path1)
        self.__wait_for_processed_files(watcher, 2)
        watcher.stop()
        assert source_path0.exists() is False
        assert source_path1.exists() is False
        assert (
            pathlib.Path(generate_config[CONFIG_DESTINATION]) / "dir1" / "test00.txt"
        ).exists() is True
        assert (
            pathlib.Path(generate_config[CONFIG_DESTINATION]) / "dir1" / "test01.txt"
        ).exists() is True
        assert watcher.files_processed == 2

    def test_watcher_copy_one_file_recursive_depth_one_keepource(
        self, generate_config: ConfigDict
    ) -> None:
        generate_config[CONFIG_RECURSIVE] = True
        generate_config[CONFIG_DELETESOURCE] = False
        watcher = Watcher(generate_config)
        watcher.start()
        source_path = pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "test.txt"
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 1)
        watcher.stop()
        assert source_path.exists() is True
        assert watcher.files_processed == 1

    def test_watcher_copy_one_file_recursive_depth_two_keepource(
        self, generate_config: ConfigDict
    ) -> None:
        generate_config[CONFIG_RECURSIVE] = True
        generate_config[CONFIG_DELETESOURCE] = False
        watcher = Watcher(generate_config)
        watcher.start()
        source_path = (
            pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "dir2" / "test.txt"
        )
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 1)
        watcher.stop()
        assert source_path.exists() is True
        assert watcher.files_processed == 1

    def test_watcher_copy_two_files_recursive_depth_one_keepource(
        self, generate_config: ConfigDict
    ) -> None:
        generate_config[CONFIG_RECURSIVE] = True
        generate_config[CONFIG_DELETESOURCE] = False
        watcher = Watcher(generate_config)
        watcher.start()
        source_path0 = (
            pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "test00.txt"
        )
        create_test_file(source_path0)
        source_path1 = (
            pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "test01.txt"
        )
        create_test_file(source_path1)
        self.__wait_for_processed_files(watcher, 2)
        watcher.stop()
        assert source_path0.exists() is True
        assert source_path1.exists() is True
        assert watcher.files_processed == 2

    def test_watcher_deletesource_source_of_depth_one(
        self, generate_config: ConfigDict
    ) -> None:
        generate_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(generate_config)
        watcher.start()
        source_path = pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "test.txt"
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 1)
        watcher.stop()
        assert (pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1").exists() is False
        assert source_path.exists() is False

    def test_watcher_deletesource_source_of_depth_two(
        self, generate_config: ConfigDict
    ) -> None:
        generate_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(generate_config)
        watcher.start()
        source_path = (
            pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "dir2" / "test.txt"
        )
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 1)
        watcher.stop()
        assert (
            pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "dir2"
        ).exists() is False
        assert (pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1").exists() is False
        assert (pathlib.Path(generate_config[CONFIG_SOURCE])).exists() is True
        assert source_path.exists() is False

    def test_watcher_deletesource_two_files_source_of_depth_two(
        self, generate_config: ConfigDict
    ) -> None:
        generate_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(generate_config)
        watcher.start()
        source_path0 = (
            pathlib.Path(generate_config[CONFIG_SOURCE])
            / "dir1"
            / "dir2"
            / "test00.txt"
        )
        create_test_file(source_path0)
        source_path1 = (
            pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "test01.txt"
        )
        create_test_file(source_path1)
        self.__wait_for_processed_files(watcher, 2)
        watcher.stop()
        assert (
            pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1" / "dir2"
        ).exists() is False
        assert (pathlib.Path(generate_config[CONFIG_SOURCE]) / "dir1").exists() is False
        assert (pathlib.Path(generate_config[CONFIG_SOURCE])).exists() is True
        assert source_path0.exists() is False
        assert source_path1.exists() is False

    def test_watcher_deletesource_one_file_root_check(
        self, generate_config: ConfigDict
    ) -> None:
        generate_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(generate_config)
        watcher.start()
        source_path = pathlib.Path(generate_config[CONFIG_SOURCE]) / "test.txt"
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 1)
        watcher.stop()
        assert (pathlib.Path(generate_config[CONFIG_SOURCE])).exists() is True
        assert source_path.exists() is False

    def test_watcher_copy_a_single_readonly_file_from_source_to_destination(
        self, generate_config: ConfigDict
    ) -> None:
        watcher = Watcher(generate_config)
        watcher.start()
        source_path = pathlib.Path(generate_config[CONFIG_SOURCE]) / "test.txt"
        create_test_file(source_path, True)
        self.__wait_for_processed_files(watcher, 1)
        watcher.stop()
        assert source_path.exists() is False
        assert (
            pathlib.Path(generate_config[CONFIG_DESTINATION]) / "test.txt"
        ).exists() is True
        assert watcher.files_processed == 1
