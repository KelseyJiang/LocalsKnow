#pull 'language' and 'city' from input field and identify the corresponding SQL datatable
def assign_datatable(lang = 'French', city = 'Paris'):
   language = lang.lower()
   city = city.lower()
   if language == 'french' and city == 'paris':
        rankby = 'fr_count'
        data_table = 'fr_den_utm_cluster_photo'
   elif language == 'english' and city == 'paris':
        rankby = 'eng_count'
        data_table = 'eng_den_utm_cluster_photo'
   else:
        rankby = 'local_count'
        data_table = 'local_den_utm_cluster_photo'
   return (data_table,rankby)
  