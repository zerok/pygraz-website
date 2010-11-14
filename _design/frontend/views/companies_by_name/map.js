function(doc) {
  if (typeof doc.doc_type !== 'undefined' && doc.doc_type === 'company'
    && (typeof doc.next_version == 'undefined' || doc.next_version == null)
    ){
    emit(doc.name, doc);
  }
}
