! function(a) {
    a.fn.gridEditor = function(b) {
        var c = this,
            d = c.data("grideditor");
        if ("getHtml" == arguments[0]) {
            if (d) {
                d.deinit();
                var e = c.html();
                return d.init(), e
            }
            return c.html()
        }
        return c.each(function(c, d) {
            function e() {
                A = d.addClass("ge-canvas"), "undefined" != typeof D && D.length || (D = a('<textarea class="ge-html-output"/>').insertBefore(A)), B = a('<div class="ge-mainControls" />').insertBefore(D);
                var b = a('<div class="ge-wrapper ge-top" />').appendTo(B);
                C = a('<div class="ge-addRowGroup btn-group" />').appendTo(b), a.each(E.new_row_layouts, function(b, c) {
                    var d = a('<a class="btn-sm btn-grid btn-square btn-grid p-10" />').attr("title", "Add row " + c.join("-")).on("click", function() {
                        var a = r().appendTo(A);
                        c.forEach(function(b) {
                            s(b).appendTo(a)
                        }), f()
                    }).appendTo(C);
                    d.append('<span class="fa fa-plus-circle"/> ' +c.join("-")+' &nbsp;&nbsp;');
                    var e = (c.join(" - "), '<div class="row ge-row-icon">');
                    c.forEach(function(a) {
                        e += '<div class="column col-' + a + '"/>'
                    }), e += "</div>",  d.append(e)
                });
                var c = a('<div class="dropdown float-start float-xl-end ge-layout-mode"><button type="button" class="btn-screen dropdown-toggle" data-toggle="dropdown"><span>Desktop</span></button><ul class="dropdown-menu" role="menu"><li><a data-width="auto" title="Desktop" class="dropdown-item"><span>Desktop</span></a></li><li><a title="Tablet" class="dropdown-item"><span>Tablet</span></li><li><a title="Phone" class="dropdown-item"><span>Phone</span></a></li></ul></div>').on("click", "a", function() {
                        var b = a(this);
                        x(b.closest("li").index());
                        var d = c.find("button");
                        d.find("span").remove(), d.append(b.find("span").clone())
                    }).appendTo(b),
                    e = a('<div class="btn-group float-start float-xl-end"/>').appendTo(b),
                    h = a('<button title="Edit Source Code" type="button" class="btn-code gm-edit-mode"><span class="fa fa-chevron-left"></span><span class="fa fa-chevron-right"></span></button>').on("click", function() {
                        h.hasClass("active") ? (A.empty().html(D.val()).show(), f(), D.hide()) : (g(), D.height(.8 * a(window).height()).val(A.html()).show(), A.hide()), h.toggleClass("active btn-danger")
                    }).appendTo(e),
                    i = a('<button title="Preview" type="button" class="btn-code gm-preview m-r-5"><span class="fa fa-eye"></span></button>').on("mouseenter", function() {
                        A.removeClass("ge-editing")
                    }).on("click", function() {
                        i.toggleClass("active btn-danger").trigger("mouseleave")
                    }).on("mouseleave", function() {
                        i.hasClass("active") || A.addClass("ge-editing")
                    }).appendTo(e),
                    j = a(window);
                // j.on("scroll", function(a) {
                //     j.scrollTop() > B.offset().top && j.scrollTop() < A.offset().top + A.height() ? b.hasClass("ge-top") && b.css({
                //         left: b.offset().left,
                //         width: b.outerWidth()
                //     }).removeClass("ge-top").addClass("ge-fixed") : b.hasClass("ge-fixed") && b.css({
                //         left: "",
                //         width: ""
                //     }).removeClass("ge-fixed").addClass("ge-top")
                // }),
                    A.on("click", ".ge-content", function(b) {
                    var c = y(a(this).data("ge-content-type"));
                    c && c.init(E, a(this))
                })
            }

            function f() {
                t(!0), A.addClass("ge-editing"), l(), u(), h(), i(), p(), x(G)
            }

            function g() {
                A.removeClass("ge-editing");
                A.find(".ge-content").each(function() {
                    var b = a(this);
                    y(b.data("ge-content-type")).deinit(E, b)
                });
                A.find(".ge-tools-drawer").remove(), q(), t()
            }

            function h() {
                A.find(".row").each(function() {
                    var b = a(this);
                    if (!b.find("> .ge-tools-drawer").length) {
                        var c = a('<div class="ge-tools-drawer" />').prependTo(b);
                        j(c, "Move", "ge-move", "fa-arrows"), j(c, "Settings", "", "fa-cog", function() {
                            d.toggle()
                        }), E.row_tools.forEach(function(a) {
                            j(c, a.title || "", a.className || "", a.iconClass || "fa-wrench", a.on)
                        }), j(c, "Remove row", "", "fa-trash", function() {
                            window.confirm("Delete row?") && b.slideUp(function() {
                                b.remove()
                            })
                        }), j(c, "Add column", "ge-add-column", "fa-plus-circle", function() {
                            b.append(s(3)), f()
                        });
                        var d = k(b, E.row_classes).appendTo(c)
                    }
                })
            }

            function i() {
                A.find(".column").each(function() {
                    var b = a(this);
                    if (!b.find("> .ge-tools-drawer").length) {
                        var c = a('<div class="ge-tools-drawer" />').prependTo(b);
                        j(c, "Move", "ge-move", "fa-arrows"), j(c, "Make column narrower\n(hold shift for min)", "ge-decrease-col-width", "fa-minus", function(a) {
                            var c = E.valid_col_sizes,
                                d = F[G],
                                e = c.indexOf(m(b, d)),
                                f = c[z(e - 1, 0, c.length - 1)];
                            a.shiftKey && (f = c[0]), o(b, d, Math.max(f, 1))
                        }), j(c, "Make column wider\n(hold shift for max)", "ge-increase-col-width", "fa-plus", function(a) {
                            var c = E.valid_col_sizes,
                                d = F[G],
                                e = c.indexOf(m(b, d)),
                                f = z(e + 1, 0, c.length - 1),
                                g = c[f];
                            a.shiftKey && (g = c[c.length - 1]), o(b, d, Math.min(g, H))
                        }), j(c, "Settings", "", "fa-cog", function() {
                            d.toggle()
                        }), E.col_tools.forEach(function(a) {
                            j(c, a.title || "", a.className || "", a.iconClass || "fa-wrench", a.on)
                        }), j(c, "Remove col", "", "fa-trash", function() {
                            window.confirm("Delete column?") && b.animate({
                                opacity: "hide",
                                width: "hide",
                                height: "hide"
                            }, 400, function() {
                                b.remove()
                            })
                        }), j(c, "Add row", "ge-add-row", "fa-plus-circle", function() {
                            var a = r();
                            b.append(a), a.append(s(6)).append(s(6)), f()
                        });
                        var d = k(b, E.col_classes).appendTo(c)
                    }
                })
            }

            function j(b, c, d, e, f) {
                var g = a('<a title="' + c + '" class="' + d + '"><span class="fa ' + e + '"></span></a>').appendTo(b);
                "function" == typeof f && g.on("click", f), "object" == typeof f && a.each(f, function(a, b) {
                    g.on(a, b)
                })
            }

            function k(b, c) {
                var d = a('<div class="ge-details" />');
                a('<input class="ge-id" />').attr("placeholder", "id").val(b.attr("id")).attr("title", "Set a unique identifier").appendTo(d).change(function() {
                    b.attr("id", this.value)
                });
                var e = a('<div class="btn-group" />').appendTo(d);
                return c.forEach(function(c) {
                    var d = a('<a class="btn btn-sm btn-default" />').html(c.label).attr("title", c.title ? c.title : 'Toggle "' + c.label + '" styling').toggleClass("active btn-primary", b.hasClass(c.cssClass)).on("click", function() {
                        d.toggleClass("active btn-primary"), b.toggleClass(c.cssClass, d.hasClass("active"))
                    }).appendTo(e)
                }), d
            }

            function l() {
                A.find('.column, div[class*="col-"]').each(function() {
                    var b = a(this),
                        c = 2,
                        d = n(b);
                    d.length && (c = d[0].size);
                    var e = b.attr("class");
                    F.forEach(function(a) {
                        -1 == e.indexOf(a) && b.addClass(a + c)
                    }), b.addClass("column")
                })
            }

            function m(a, b) {
                for (var c = n(a), d = 0; d < c.length; d++)
                    if (c[d].colClass == b) return c[d].size;
                return c.length ? c[0].size : null
            }

            function n(a) {
                var b = [];
                return F.forEach(function(c) {
                    var d = new RegExp(c + "(\\d+)", "i");
                    d.test(a.attr("class")) && b.push({
                        colClass: c,
                        size: parseInt(d.exec(a.attr("class"))[1])
                    })
                }), b
            }

            function o(a, b, c) {
                var d = new RegExp("(" + b + "(\\d+))", "i"),
                    e = d.exec(a.attr("class"));
                e && parseInt(e[2]) !== c ? a.switchClass(e[1], b + c, 50) : a.addClass(b + c)
            }

            function p() {
                function a(a, b) {
                    b.placeholder.css({
                        height: b.item.outerHeight()
                    })
                }
                A.find(".row").sortable({
                    items: "> .column",
                    connectWith: ".ge-canvas .row",
                    handle: "> .ge-tools-drawer .ge-move",
                    start: a,
                    helper: "clone"
                }), A.add(A.find(".column")).sortable({
                    items: "> .row, > .ge-content",
                    connectsWith: ".ge-canvas, .ge-canvas .column",
                    handle: "> .ge-tools-drawer .ge-move",
                    start: a,
                    helper: "clone"
                })
            }

            function q() {
                A.add(A.find(".column")).add(A.find(".row")).sortable("destroy")
            }

            function r() {
                return a('<div class="row" />')
            }

            function s(b) {
                return a("<div/>").addClass(F.map(function(a) {
                    return a + b
                }).join(" ")).append(w().html(y(E.content_types[0]).initialContent))
            }

            function t(b) {
                E.custom_filter.length && a.each(E.custom_filter, function(a, c) {
                    "string" == typeof c && (c = window[c]), c(A, b)
                })
            }

            function u() {
                A.find(".column").each(function() {
                    var b = a(this),
                        c = a();
                    b.children().each(function() {
                        var b = a(this);
                        b.is(".row, .ge-tools-drawer, .ge-content") ? v(c) : c = c.add(b)
                    }), v(c)
                })
            }

            function v(b) {
                if (b.length) {
                    var c = w().insertAfter(b.last());
                    b.appendTo(c), b = a()
                }
            }

            function w() {
                return a("<div/>").addClass("ge-content ge-content-type-" + E.content_types[0]).attr("data-ge-content-type", E.content_types[0])
            }

            function x(a) {
                G = a;
                var b = ["ge-layout-desktop", "ge-layout-tablet", "ge-layout-phone"];
                b.forEach(function(b, c) {
                    A.toggleClass(b, c == a)
                })
            }

            function y(b) {
                return a.fn.gridEditor.RTEs[b]
            }

            function z(a, b, c) {
                return Math.min(c, Math.max(b, a))
            }
            d = a(d);
            var A, B, C, D, E = a.extend({
                    new_row_layouts: [
                        [12],
                        [6, 6],
                        [4, 4, 4],
                        [3, 3, 3, 3],
                        [2, 2, 2, 2, 2, 2],
                        [2, 8, 2],
                        [4, 8],
                        [8, 4]
                    ],
                    row_classes: [{
                        label: "Example class",
                        cssClass: "example-class"
                    }],
                    col_classes: [{
                        label: "Example class",
                        cssClass: "example-class"
                    }],
                    col_tools: [],
                    row_tools: [],
                    custom_filter: "",
                    content_types: ["tinymce"],
                    valid_col_sizes: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    source_textarea: ""
                }, b),
                F = ["col-md-", "col-sm-", "col-"],
                G = 0,
                H = 12;
            if (E.source_textarea) {
                var I = a(E.source_textarea);
                I.addClass("ge-html-output"), D = I, I.val() && d.html(I.val())
            }
            if (d.children().length && !d.find("div.row").length) {
                var J = d.children(),
                    K = a('<div class="row"><div class="col-md-12"/></div>').appendTo(d);
                K.find(".col-md-12").append(J)
            }
            e(), f(), d.data("grideditor", {
                init: f,
                deinit: g
            })
        }), c
    }, a.fn.gridEditor.RTEs = {}
}(jQuery),
    function() {
        $.fn.gridEditor.RTEs.ckeditor = {
            init: function(a, b) {
                window.CKEDITOR || console.error("CKEditor not available! Make sure you loaded the ckeditor and jquery adapter js files.");
                var c = this;
                b.each(function() {
                    var b = $(this);
                    if (!b.hasClass("active")) {
                        b.html() == c.initialContent && b.html("&nbsp;"), b.addClass("active").attr("contenteditable", "true");
                        var d = $.extend({}, a.ckeditor && a.ckeditor.config ? a.ckeditor.config : {}, {
                                on: {
                                    instanceReady: function(b) {
                                        var c;
                                        try {
                                            c = a.ckeditor.config.on.instanceReady
                                        } catch (d) {}
                                        c && c.call(this, b), e.focus()
                                    }
                                }
                            }),
                            e = CKEDITOR.inline(b.get(0), d)
                    }
                })
            },
            deinit: function(a, b) {
                b.filter(".active").each(function() {
                    var a = $(this);
                    $.each(CKEDITOR.instances, function(a, b) {
                        b.destroy()
                    }), a.removeClass("active cke_focus").removeAttr("id").removeAttr("style").removeAttr("spellcheck").removeAttr("contenteditable")
                })
            },
            initialContent: "<p>Lorem initius... </p>"
        }
    }(),
    function() {
        $.fn.gridEditor.RTEs.summernote = {
            init: function(a, b) {
                jQuery().summernote || console.error("Summernote not available! Make sure you loaded the Summernote js file.");
                var c = this;
                b.each(function() {
                    var b = $(this);
                    if (!b.hasClass("active")) {
                        b.html() == c.initialContent && b.html(""), b.addClass("active");
                        var d = $.extend(!0, {}, a.summernote && a.summernote.config ? a.summernote.config : {}, {
                            tabsize: 2,
                            airMode: !0,
                            callbacks: {
                                onInit: function() {
                                    var c;
                                    try {
                                        c = a.summernote.config.callbacks.onInit
                                    } catch (d) {}
                                    c && c.call(this), b.summernote("focus")
                                }
                            }
                        });
                        b.summernote(d)
                    }
                })
            },
            deinit: function(a, b) {
                b.filter(".active").each(function() {
                    var a = $(this);
                    a.summernote("destroy"), a.removeClass("active").removeAttr("id").removeAttr("style").removeAttr("spellcheck")
                })
            },
            initialContent: "<p>Lorem ipsum dolores</p>"
        }
    }(),
    function() {
        $.fn.gridEditor.RTEs.tinymce = {
            init: function(a, b) {
                window.tinymce || console.error("tinyMCE not available! Make sure you loaded the tinyMCE js file."), b.tinymce || console.error("tinyMCE jquery integration not available! Make sure you loaded the jquery integration plugin.");
                var c = this;
                b.each(function() {
                    var b = $(this);
                    if (!b.hasClass("active")) {
                        b.html() == c.initialContent && b.html(""), b.addClass("active");
                        var d = $.extend({}, a.tinymce && a.tinymce.config ? a.tinymce.config : {}, {
                            inline: !0,
                            oninit: function(b) {
                                $("#" + b.settings.id).focus();
                                var c;
                                try {
                                    c = a.tinymce.config.oninit
                                } catch (d) {}
                                c && c.call(this)
                            }
                        });
                        b.tinymce(d)
                    }
                })
            },
            deinit: function(a, b) {
                b.filter(".active").each(function() {
                    var a = $(this),
                        b = a.tinymce();
                    b && b.remove(), a.removeClass("active").removeAttr("id").removeAttr("style").removeAttr("spellcheck")
                })
            },
            initialContent: "<p>Lorem ipsum dolores</p>"
        }
    }();
//# sourceMappingURL=jquery.grideditor.min.js.map