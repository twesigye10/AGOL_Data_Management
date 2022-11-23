# importing modules
import os
import re
from arcgis.gis import GIS
# credentials stored in a separate file
import support_files.credentials as cred

try:
    # Establish connection
    # gis = GIS("portal url", "username","password")
    p_url = cred.portal_url
    p_user = cred.portal_user
    pass_user = cred.portal_user_pass

    gis_portal = GIS(p_url, username=p_user, password=pass_user)
    print("Connected to the following portal : {0} ".format(p_url))
    #
    fs_title = 'tax_components_admin'
    fs_owner = p_user # here you can provide the owner of the layer

    query_string = 'title: ' + fs_title + ' AND owner: ' + fs_owner
    search_result = gis_portal.content.search(query=query_string, item_type="Feature Layer")
    print("Data search : {0} ".format(search_result))
    data_interest = search_result[0]

    if data_interest:
        print("Item with id : {0} ".format(data_interest.id))
        # lyr_for_update = data_interest.layers[7]
        lyr_for_update = data_interest.layers[0]
        print("Active layer : {0} ".format(lyr_for_update.properties.name))
        ## Check if the layer allows editing
        update_lyr_capabilities = lyr_for_update.properties.capabilities
        update_lyr_attachments_enabled = lyr_for_update.properties.hasAttachments
        print("Capabilities of the layer : {0} ".format(update_lyr_capabilities))
        print("Has attachments : {0} ".format(update_lyr_attachments_enabled))

        if "Update" in update_lyr_capabilities and update_lyr_attachments_enabled == True:
            # Attachments location
            src_dir = "D:\\Upwork\\Taxation Dashboard\\Photos of research\\photo_attach\\photo_attach_id_number\\"
            for count, filename in enumerate(os.listdir(src_dir)):
                # parent_OID = int(filename.split("_")[0])
                parent_id_number = filename.split("_")[0]
                # query using id_number
                id_query_string = "component='Industrial' and id_number=" + parent_id_number
                # id_query_string = "id_number=" + parent_id_number
                query_data = lyr_for_update.query(where=id_query_string, out_fields='OBJECTID,id_number,case_id', returnGeometry='false')
                # print("Active feature has data : {0} ".format(query_data))

                available_fts = query_data.features

                if len(available_fts) > 0:
                    ft_update = available_fts[0]
                    ## Edit photo description
                    # name_without_extension = filename.split(".")[0]
                    # # attr_update_txt = name_no_extension.split("_")[1] + "_" + name_no_extension.split("_")[2]
                    # attr_update_txt = name_without_extension.split("_")[1] + "_" + re.sub("[a-zA-Z]$", "", name_without_extension.split("_")[2])
                    # # print("The attribute for the photo_attach field is : {0}  ".format(attr_update_txt))
                    # current_attr_value = ft_update.attributes['photo_attach']
                    # if len(current_attr_value) < 1:
                    #     ft_update.attributes['photo_attach'] = attr_update_txt
                        # lyr_for_update.edit_features(updates=[ft_update])
                    ## Attach photo
                    parent_OID = ft_update.attributes['OBJECTID']
                    # print("The object_id of the current feature is : {0}  ".format(parent_OID))
                    photo_path = src_dir + filename
                    lyr_for_update.attachments.add(parent_OID, photo_path)
                    print("Feature with OID : {0} , updated with image with name : {1} ".format(parent_OID, filename))

            print("""
            ************************************************************************
            ****    Congrats!!!! Finished processing updates and attachments    ****
            ************************************************************************
            """)
        else:
           print("Ensure the layers has Update capabilities. You also need to enable Attachments under the item details of the Feature Layer")
    else:
        print("Layer doesn't exist")

except Exception as err:
    print(err.args[0])
