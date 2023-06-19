import pytest
import time
import pathlib

from tests.common import create_test_file, create_watcher_config
from core.constants import CONFIG_SOURCE, CONFIG_DESTINATION, CONFIG_DELETESOURCE, CONFIG_RECURSIVE
from core.config import ConfigDict
from core.watcher import Watcher, WatcherError
from core.factory import Factory
from builtin.copyfile_handler import CopyFileHandler
from builtin.sftp_copyfile_handler import SFTPCopyFileHandler


@pytest.fixture()
def watcher_config() -> ConfigDict:

    Factory.clear()
    Factory.register("CopyFile", CopyFileHandler)
    Factory.register("SFTPCopyFile", SFTPCopyFileHandler)

    yield create_watcher_config()


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
            assert (destination_path /
                    f"test{file_number}.txt").exists() == True
        watcher.stop()

    def test_watcher_with_config_of_none(self) -> None:
        with pytest.raises(WatcherError):
            _ = Watcher(None)  # type: ignore

    def test_watcher_inlaid_config(self, watcher_config: ConfigDict) -> None:
        watcher_config.pop(CONFIG_DESTINATION)
        with pytest.raises(WatcherError):
            _ = Watcher(watcher_config)

    def test_watcher_with_a_valid_config(self, watcher_config: ConfigDict) -> None:
        watcher = Watcher(watcher_config)
        assert watcher != None

    def test_watcher_with_a_valid_config_check_source_directory(self, watcher_config: ConfigDict) -> None:
        assert pathlib.Path(
            watcher_config[CONFIG_SOURCE]).exists() == False
        watcher = Watcher(watcher_config)
        assert pathlib.Path(
            watcher_config[CONFIG_SOURCE]).exists() == True

    def test_watcher_with_a_valid_config_check_desination_directory(self, watcher_config: ConfigDict) -> None:
        assert pathlib.Path(
            watcher_config[CONFIG_DESTINATION]).exists() == False
        watcher = Watcher(watcher_config)
        assert pathlib.Path(
            watcher_config[CONFIG_DESTINATION]).exists() == True

    def test_watcher_initial_state_stopped(self, watcher_config: ConfigDict) -> None:
        watcher = Watcher(watcher_config)
        assert watcher.is_running == False

    def test_watcher_started(self, watcher_config: ConfigDict):
        watcher = Watcher(watcher_config)
        watcher.start()
        assert watcher.is_running == True

    def test_watcher_start_a_running_watcher(self, watcher_config: ConfigDict) -> None:
        watcher = Watcher(watcher_config)
        watcher.start()
        watcher.start()
        assert watcher.is_running == True

    def test_watcher_stopping_a_stopped_watcher(self, watcher_config: ConfigDict) -> None:
        watcher = Watcher(watcher_config)
        watcher.start()
        watcher.stop()
        watcher.stop()
        assert watcher.is_running == False

    def test_watcher_started_then_stopped(self, watcher_config: ConfigDict) -> None:
        watcher = Watcher(watcher_config)
        watcher.start()
        time.sleep(1)
        watcher.stop()
        assert watcher.is_running == False

    def test_watcher_started_then_stopped_then_restarted(self, watcher_config: ConfigDict) -> None:
        watcher = Watcher(watcher_config)
        watcher.start()
        time.sleep(1)
        watcher.stop()
        watcher.start()
        assert watcher.is_running == True

    def test_watcher_copy_a_single_file_from_source_to_destination(self, watcher_config: ConfigDict) -> None:
        self.__copy_count_files(watcher_config, 1)
        assert (pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / f"test0.txt").exists() == False

    def test_watcher_copy_a_single_file_from_source_to_destination_keepsource(self, watcher_config: ConfigDict) -> None:
        watcher_config[CONFIG_DELETESOURCE] = False
        self.__copy_count_files(watcher_config, 1)
        assert (pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / f"test0.txt").exists() == True

    def test_watcher_copy_ten_files_from_source_to_destination(self, watcher_config: ConfigDict) -> None:
        self.__copy_count_files(watcher_config, 10)

    def test_watcher_copy_fifty_files_from_source_to_destination(self, watcher_config: ConfigDict) -> None:
        self.__copy_count_files(watcher_config, 50)

    def test_watcher_copy_onehundred_files_from_source_to_destination(self, watcher_config: ConfigDict) -> None:
        self.__copy_count_files(watcher_config, 100)

    def test_watcher_copy_onethousand_files_from_source_to_destination(self, watcher_config: ConfigDict) -> None:
        self.__copy_count_files(watcher_config, 1000)

    def test_watcher_copy_one_file_recursive_depth_one_deletesource(self, watcher_config: ConfigDict) -> None:
        watcher_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(watcher_config)
        watcher.start()
        source_path = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "test.txt"
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 2)
        watcher.stop()
        assert source_path.exists() == False
        assert (pathlib.Path(
            watcher_config[CONFIG_DESTINATION]) / "dir1" / "test.txt").exists() == True
        assert watcher.files_processed == 2

    def test_watcher_copy_one_file_recursive_depth_two_deletesource(self, watcher_config: ConfigDict) -> None:
        watcher_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(watcher_config)
        watcher.start()
        source_path = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "dir2" / "test.txt"
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 3)
        watcher.stop()
        assert source_path.exists() == False
        assert (pathlib.Path(
            watcher_config[CONFIG_DESTINATION]) / "dir1" / "dir2" / "test.txt").exists() == True
        assert watcher.files_processed == 3

    def test_watcher_copy_two_files_recursive_depth_one_deletesource(self, watcher_config: ConfigDict) -> None:
        watcher_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(watcher_config)
        watcher.start()
        source_path0 = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "test00.txt"
        create_test_file(source_path0)
        source_path1 = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "test01.txt"
        create_test_file(source_path1)
        self.__wait_for_processed_files(watcher, 3)
        watcher.stop()
        assert source_path0.exists() == False
        assert source_path1.exists() == False
        assert (pathlib.Path(
            watcher_config[CONFIG_DESTINATION]) / "dir1" / "test00.txt").exists() == True
        assert (pathlib.Path(
            watcher_config[CONFIG_DESTINATION]) / "dir1" / "test01.txt").exists() == True
        assert watcher.files_processed == 3

    def test_watcher_copy_one_file_recursive_depth_one_keepource(self, watcher_config: ConfigDict) -> None:
        watcher_config[CONFIG_RECURSIVE] = True
        watcher_config[CONFIG_DELETESOURCE] = False
        watcher = Watcher(watcher_config)
        watcher.start()
        source_path = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "test.txt"
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 2)
        watcher.stop()
        assert source_path.exists() == True
        assert (pathlib.Path(
            watcher_config[CONFIG_DESTINATION]) / "dir1" / "test.txt").exists() == True
        assert watcher.files_processed == 2

    def test_watcher_copy_one_file_recursive_depth_two_keepource(self, watcher_config: ConfigDict) -> None:
        watcher_config[CONFIG_RECURSIVE] = True
        watcher_config[CONFIG_DELETESOURCE] = False
        watcher = Watcher(watcher_config)
        watcher.start()
        source_path = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "dir2" / "test.txt"
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 3)
        watcher.stop()
        assert source_path.exists() == True
        assert (pathlib.Path(
            watcher_config[CONFIG_DESTINATION]) / "dir1" / "dir2" / "test.txt").exists() == True
        assert watcher.files_processed == 3

    def test_watcher_copy_two_files_recursive_depth_one_keepource(self, watcher_config: ConfigDict) -> None:
        watcher_config[CONFIG_RECURSIVE] = True
        watcher_config[CONFIG_DELETESOURCE] = False
        watcher = Watcher(watcher_config)
        watcher.start()
        source_path0 = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "test00.txt"
        create_test_file(source_path0)
        source_path1 = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "test01.txt"
        create_test_file(source_path1)
        self.__wait_for_processed_files(watcher, 3)
        watcher.stop()
        assert source_path0.exists() == True
        assert source_path1.exists() == True
        assert (pathlib.Path(
            watcher_config[CONFIG_DESTINATION]) / "dir1" / "test00.txt").exists() == True
        assert (pathlib.Path(
            watcher_config[CONFIG_DESTINATION]) / "dir1" / "test01.txt").exists() == True
        assert watcher.files_processed == 3

    def test_watcher_deletesource_source_of_depth_one(self, watcher_config: ConfigDict) -> None:
        watcher_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(watcher_config)
        watcher.start()
        source_path = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "test.txt"
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 2)
        watcher.stop()
        assert (pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1").exists() == False
        assert (pathlib.Path(
            watcher_config[CONFIG_SOURCE])).exists() == True
        assert source_path.exists() == False

    def test_watcher_deletesource_source_of_depth_two(self, watcher_config: ConfigDict) -> None:
        watcher_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(watcher_config)
        watcher.start()
        source_path = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "dir2" / "test.txt"
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 3)
        watcher.stop()
        assert (pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "dir2").exists() == False
        assert (pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1").exists() == False
        assert (pathlib.Path(
                watcher_config[CONFIG_SOURCE])).exists() == True
        assert source_path.exists() == False

    def test_watcher_deletesource_two_files_source_of_depth_two(self, watcher_config: ConfigDict) -> None:
        watcher_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(watcher_config)
        watcher.start()
        source_path0 = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "dir2" / "test00.txt"
        create_test_file(source_path0)
        source_path1 = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "test01.txt"
        create_test_file(source_path1)
        self.__wait_for_processed_files(watcher, 3)
        watcher.stop()
        assert (pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1" / "dir2").exists() == False
        assert (pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "dir1").exists() == False
        assert (pathlib.Path(
                watcher_config[CONFIG_SOURCE])).exists() == True
        assert source_path0.exists() == False
        assert source_path1.exists() == False

    def test_watcher_deletesource_one_file_root_check(self, watcher_config: ConfigDict) -> None:
        watcher_config[CONFIG_RECURSIVE] = True
        watcher = Watcher(watcher_config)
        watcher.start()
        source_path = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "test.txt"
        create_test_file(source_path)
        self.__wait_for_processed_files(watcher, 1)
        watcher.stop()
        assert (pathlib.Path(
            watcher_config[CONFIG_SOURCE])).exists() == True
        assert source_path.exists() == False

    def test_watcher_copy_a_single_readonly_file_from_source_to_destination(self, watcher_config: ConfigDict) -> None:
        watcher = Watcher(watcher_config)
        watcher.start()
        source_path = pathlib.Path(
            watcher_config[CONFIG_SOURCE]) / "test.txt"
        create_test_file(source_path, True)
        self.__wait_for_processed_files(watcher, 1)
        watcher.stop()
        assert source_path.exists() == False
        assert (pathlib.Path(
            watcher_config[CONFIG_DESTINATION]) / "test.txt").exists() == True
        assert watcher.files_processed == 1
