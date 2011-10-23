import blinker

namespace = blinker.Namespace()

meetup_created = namespace.signal('meetup-created')
meetup_changed = namespace.signal('meetup-changed')
meetup_deleted = namespace.signal('meetup-deleted')
sessionidea_created = namespace.signal('sessionidea-created')
sessionidea_changed = namespace.signal('sessionidea-changed')
sessionidea_deleted = namespace.signal('sessionidea-deleted')
sessionidea_voted = namespace.signal('sessionidea-voted')
sessionidea_unvoted = namespace.signal('sessionidea-unvoted')
