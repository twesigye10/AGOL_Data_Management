# importing modules
import os
from arcgis.gis import GIS
# credentials stored in a separate file
import support_files.credentials as cred

try:
    # gis = GIS("portal url", "username","password")
    p_url = cred.portal_url
    p_token = cred.token
    gis = GIS(p_url, token=p_token)
    print("Connected to the following portal : {0} ".format(p_url))
    #
    fs_title = 'luzira_landlplot_dashboard1'
    fs_owner = 'steph202'

    # fs_title = 'dashboard___Luzira_landlplot_admin_bound'
    # fs_owner = 'uganda_creator'

    query_string = 'title: ' + fs_title + ' AND owner: ' + fs_owner
    search_result = gis.content.search(query=query_string, item_type="Feature Layer")
    data_interest = search_result[0]

    if data_interest:
        print("Finished searching id : {0} ".format(data_interest.id))
        lyr_for_update = data_interest.layers[0]
        print("Active layer : {0} ".format(lyr_for_update.properties.name))
        query_data = lyr_for_update.query(where="1=1", out_fields='OBJECTID,id_number,case_id', returnGeometry='false')
        # print("Query data : {0} ".format(query_data))
        # put appropriate folder locations
        src_dir = "D:\\xxxx\\xxxx\\Photos of research\\photo_attach\\photo_attach\\"
        dst_dir = "D:\\xxxx\\xxxx\\Photos of research\\photo_attach\\photo_attach_id_number\\"

        available_fts = query_data.features
        # print("Available features: {0} ".format(available_fts))

        for ft in available_fts:
            parent_OID = ft.attributes["OBJECTID"]
            parent_id_number = ft.attributes["id_number"]
            # print("Current feature: {0} ".format(ft))
            for count, filename in enumerate(os.listdir(src_dir)):
                desired_name = str(parent_id_number) + "_" + filename.split("_")[1] + "_" + filename.split("_")[2]
                if filename.split("_")[0] == str(parent_OID):
                    print("Desired name: {0} , Current name: {1}".format(desired_name,filename))
                    # rename all the files
                    os.rename(src_dir+filename , dst_dir+desired_name)
    else:
        print("Layer doesn't exist")

except Exception as err:
    print(err.args[0])
