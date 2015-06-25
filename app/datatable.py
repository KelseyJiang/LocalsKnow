#take group label from input.html and identify the corresponding SQL datatable
def assign_datatable(lang):
   if lang == 'french':
        rankby = 'fr_count'
        data_table = 'fr_den_utm_cluster_photo'
   elif lang == 'english':
        rankby = 'eng_count'
        data_table = 'eng_den_utm_cluster_photo'
   else:
        rankby = 'local_count'
        data_table = 'local_den_utm_cluster_photo'
   return (data_table,rankby)
  