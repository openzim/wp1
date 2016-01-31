select pl_title
  from pagelinks join page on pl_from = page_id
 where page_namespace = 0 
   and page_title = 'List_of_decades';

