function(doc) {
  if (typeof doc.doc_type !== 'undefined' && doc.doc_type === 'meetup' && (typeof doc.next_version === 'undefined' || doc.next_version == null)){
    emit(doc.start.split("T")[0], {
	start: doc.start,
	end: doc.end,
	location: doc.location
    });
  }
}
