#pull 'language' and 'city' from input field and identify the corresponding SQL datatable
def assign_datatable(lang = 'French', city = 'Paris'):
   language = lang.lower()
   city = city.lower()
   if language == 'french' and city == 'paris':
        data_table = 'fr_den_utm_cluster'
   elif language == 'english' and city == 'paris':
        data_table = 'eng_den_utm_cluster'
   else:
        data_table = 'fr_den_utm_cluster'
   return data_table
  