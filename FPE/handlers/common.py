import logging

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


def _display_details(handler_section):
    """Display event handler details and paraneters."""
    
    logging.info('*' * 80)
    logging.info('{name} Handler [{type}] running...'.format(**handler_section))
    for option in handler_section.keys():
        if option != 'name' and option != 'type':
            logging.info('{} = {}'.format(option, handler_section[option]))
            
            
def _update_row(table_name, key, row):
    """Generate SQL for update/insert row of fields."""
  
    fields = ''     
   
    # Key provided then doing update
     
    if key != '':
        
        for field in row.keys():
            fields += '{} = \'{}\','.format(field,
                                            row[field].replace("'", "''"))
            
        fields = fields[:-1]
        
        sql = 'UPDATE {} SET {} WHERE {} = {}'.format(table_name,
                                                      fields, key, row[key])
    
    # Doing an insert of a new record
       
    else:  
           
        values = ''
        for field in row.keys():
            fields += '{},'.format(field)
            values += '\'{}\','.format(row[field].replace("'", "''"))
    
        fields, values = fields[:-1], values[:-1]
     
        sql = 'INSERT INTO {} ({}) VALUES ({})'.format(table_name,
                                                       fields, values)
    
    logging.debug(sql)
    
    return (sql)
