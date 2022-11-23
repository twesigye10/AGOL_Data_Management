# importing modules
import os
import re
import requests
from arcgis.gis import GIS
# credentials stored in a separate file
import support_files.credentials as cred

"""
query layer and delete some features 

"""

try:
    ## Establish connection
    # gis = GIS("portal url", "username","password")
    p_url = cred.portal_url
    gis = GIS(p_url, token=cred.token)
    print("Connected to the following portal : {0} ".format(p_url))
    #
    fs_title_to_update = input("Enter Feature service name to delete features from : ") or cred.delete_buildings
    fs_owner_to_update = input('Enter owner of data with required values : ') or cred.portal_user

    query_string_to_update = 'title: ' + fs_title_to_update + ' AND owner: ' + fs_owner_to_update
    search_result_to_update = gis.content.search(query=query_string_to_update, item_type="Feature Layer")
    data_interest_to_update = search_result_to_update[0]

    nakawa_geom = []
    central_geom = []

    if data_interest_to_update:
        lyr_to_update = data_interest_to_update.layers[0]
        print("Update layer name : {0} ".format(lyr_to_update.properties.name))
        ## Check if the layer allows editing
        update_lyr_capabilities = lyr_to_update.properties.capabilities
        print("Capabilities of the Update layer : {0} ".format(update_lyr_capabilities))

        if "Delete" in update_lyr_capabilities:
            # print("Properties of the Update layer : {0} ".format(lyr_to_update.properties))
            record_count_lyr_to_update = lyr_to_update.query(where='1=1', return_count_only="true")
            print("The total record count in the layer to delete features is : {0}".format(record_count_lyr_to_update))
            result_offset_with_values = lyr_to_update.properties.maxRecordCount
            # Query Ids
            oids_all_feature = lyr_to_update.query(where='1=1', return_ids_only="true")

            oids_nakawa = lyr_to_update.query(geometry_filter=nakawa_geom, return_ids_only='true')
            oids_central = lyr_to_update.query(geometry_filter=central_geom, return_ids_only='true')
            # oids_within_area_interest =

            print(oids_central["objectIds"])
            oids_all_feature_list = oids_all_feature["objectIds"]
            oids_nakawa_list = oids_nakawa["objectIds"]
            oids_central_list = oids_central["objectIds"]


            index = 0
            # while index < 40:
            for oid_data in oids_all_feature_list:
                if oid_data not in oids_nakawa_list and oid_data not in oids_central_list:
                    # query data to delete
                    query_update_string = 'OBJECTID=' + str(oid_data)
                    print("Query String : {0} ".format(query_update_string))
                    query_update_data = lyr_to_update.query(where=query_update_string, out_fields='*', returnGeometry='true')
                    update_fts = query_update_data.features
                    ft_update = update_fts[0]
                    # lyr_to_update.delete_features(deletes=[ft_update])
                    print("Feature deleted with oid : {0} ".format(oid_data))

                if index >= 50:
                    break

                index += 1

            print("""
            ****        Congrats!!!!        Finished processing deletes         ****
            """)

        else:
            print("The update layer does not have update capabilities")
    else:
        print("Both Layers do not exist")

except Exception as err:
    print(err.args[0])
