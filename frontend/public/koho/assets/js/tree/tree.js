'use strict';
var tree_custom = {
    init: function() {
        $('#treeBasic').jstree({
            'core' : {
                'themes' : {
                    'responsive': false
                }
            },
            'types' : {
                'default' : { 
                    'icon' : 'icofont icofont-folder font-theme'
                },
                'file' : {
                    'icon' : 'icofont icofont-file-alt font-dark'
                }
            },
            'plugins' : ['types']
        }), $('#treecheckbox').jstree({
    		'core' : {
    			'themes' : {
    				'responsive': false
    			}
    		},
            'types' : {
                'default' : {
                    'icon' : 'icofont icofont-folder font-theme'
                },
                'file' : {
                    'icon' : 'icofont icofont-file-alt font-dark'
                }
            },
            'plugins' : ['types', 'checkbox']
        }), $('#dragTree').jstree({
    		'core' : {
    			'check_callback' : true,
    			'themes' : {
    				'responsive': false
    			}
    		},
            'types' : {
                'default' : {
                    'icon' : 'icofont icofont-folder  font-theme'
                },
                'file' : {
                    'icon' : 'icofont icofont-file-alt font-dark'
                }
            },
            'plugins' : ['types', 'dnd']
        }), $('#contextmenu').jstree({
            'core' : {
                'check_callback' : true,
                'themes' : {
                    'responsive': false
                }
            },
            'types' : {
                'default' : {
                    'icon' : 'icofont icofont-folder  font-theme'
                },
                'file' : {
                    'icon' : 'icofont icofont-file-alt font-dark'
                }
            },
                    "plugins" : [ "contextmenu", "state", "types" ]
        });
    }
};
(function($) {
    "use strict";
    tree_custom.init()
})(jQuery);