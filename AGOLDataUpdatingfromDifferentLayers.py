# importing modules
import os
import re
import requests
from arcgis.gis import GIS
# credentials stored in a separate file
import support_files.credentials as cred

try:
    ## Establish connection
    # gis = GIS("portal url", "username","password")
    p_url = cred.portal_url
    gis = GIS(p_url, token=cred.token)
    print("Connected to the following portal : {0} ".format(p_url))

    fs_title_to_update = 'tax_components_admin'
    fs_owner_to_update = cred.portal_user

    fs_title_with_values = input("Enter Feature service name : ")
    fs_owner_with_values = input('Enter owner of data with required values : ') or cred.portal_user

    # fields to process
    # update_field = "tax_due"
    # available_field = "tax_due"
    # id_field1 = "id_number"
    # id_field2 = "case_id"

    update_field = "tax_due"
    available_field = input("Enter field to copy data from like 'tax_due' : ")
    id_field1 = input("Enter first id field like 'id_number' : ")
    id_field2 = input("Enter second id field like 'case_id' : ")

    query_string_to_update = 'title: ' + fs_title_to_update + ' AND owner: ' + fs_owner_to_update
    search_result_to_update = gis.content.search(query=query_string_to_update, item_type="Feature Layer")
    data_interest_to_update = search_result_to_update[0]

    query_string_with_values = 'title: ' + fs_title_with_values + ' AND owner: ' + fs_owner_with_values
    search_result_with_values = gis.content.search(query=query_string_with_values, item_type="Feature Layer")
    # data_interest_with_values = search_result_with_values[0]
    # search for "dashboard" for old data from stephanie
    data_interest_with_values = search_result_with_values[1]

    if data_interest_to_update and data_interest_with_values:
        print("Item to update has id : {0} ".format(data_interest_to_update.id))
        print("Item with values has id : {0} ".format(data_interest_with_values.id))
        #
        lyr_to_update = data_interest_to_update.layers[0]
        print("Update layer name : {0} ".format(lyr_to_update.properties.name))
        # lyr_with_values = data_interest_with_values.layers[0]
        # use (layer endpoint index -1)
        lyr_with_values = data_interest_with_values.layers[8]
        print("Values layer name : {0} ".format(lyr_with_values.properties.name))

        ## Check if the layer allows editing
        update_lyr_capabilities = lyr_to_update.properties.capabilities
        print("Capabilities of the Update layer : {0} ".format(update_lyr_capabilities))

        if "Update" in update_lyr_capabilities:
            # print("Properties of the Update layer : {0} ".format(lyr_to_update.properties))
            record_count_lyr_with_values =  lyr_with_values.query(where='1=1', return_count_only="true")
            print("The total record count in the layer is : {0}".format(record_count_lyr_with_values))
            result_offset_with_values = lyr_with_values.properties.maxRecordCount

            index = 0
            while index < record_count_lyr_with_values:
                # start_value_str = '"' + index + '"'
                # print("The current index to start query is : {0} , with type : {1}".format(index, type(index)))
                # construct query
                query_available_data = lyr_with_values.query(where='1=1', out_fields='*', return_geometry="false", result_offset=index, return_all_records='false')
                # print("Active feature has data : {0} ".format(query_data))

                available_fts = query_available_data.features
                # print("Available features are : {0}".format(available_fts))

                for av_ft in available_fts:
                    available_tax_due_attr_value = av_ft.attributes[available_field]
                    id_field1_attr_value = av_ft.attributes[id_field1]
                    id_field2_attr_value = av_ft.attributes[id_field2]
                    # component_attr_value = av_ft.attributes['component']
                    # print("id_number value : {0} , case_id value : {1}".format(id_attr_value, case_attr_value))
                    if available_tax_due_attr_value:
                        # query using id_number
                        query_update_string = id_field1 + '=' + str(id_field1_attr_value) + " AND " + id_field2 +'=' + "'" + id_field2_attr_value + "'"
                        query_fields_string = id_field1 + ',' + id_field2 + ',' + update_field
                        print("Query String : {0} ".format(query_update_string))
                        query_update_data = lyr_to_update.query(where=query_update_string, out_fields=query_fields_string, returnGeometry='false')
                        update_fts = query_update_data.features
                        ft_update = update_fts[0]
                        update_tax_due_attr_value = ft_update.attributes[update_field]
                        if update_tax_due_attr_value is None:
                            ft_update.attributes[update_field] = available_tax_due_attr_value
                            lyr_to_update.edit_features(updates=[ft_update])
                            print("Feature with {0} : {1} , and {2} : {3}  , updated with with {4} : {5} ".format(id_field1, id_field1_attr_value, id_field2, id_field2_attr_value, update_field, available_tax_due_attr_value))

                index += result_offset_with_values

            print("""
            ************************************************************************
            ****        Congrats!!!!        Finished processing updates         ****
            ************************************************************************
            """)

        else:
            print("The update layer does not have update capabilities")
    else:
        print("Both Layers do not exist")

except Exception as err:
    print(err.args[0])
