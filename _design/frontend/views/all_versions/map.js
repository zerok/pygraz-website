function(doc) {
  if (typeof doc.root_id !== 'undefined')
  emit([doc.root_id, doc.updated_at], {
    "updated_at":doc.updated_at,
    "_id": doc._id,
    "next_version": doc.next_version,
    "previous_version": doc.previous_version
  });
}
