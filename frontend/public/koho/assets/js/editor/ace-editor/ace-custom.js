"use strict";

var editor = ace.edit("editor");
// Sublime appearance:
editor.setTheme("ace/theme/monokai");

// You may choose from many many language syntaxes or let syntax default
editor.getSession().setMode("ace/mode/javascript");

// More editor properties can be set here ...

// HTML editor
var html_editor = ace.edit("html-editor");
html_editor.setTheme("ace/theme/monokai");
html_editor.getSession().setMode("ace/mode/html");
html_editor.setShowPrintMargin(false);


// CSS editor
var css_editor = ace.edit("css-editor");
css_editor.setTheme("ace/theme/monokai");
css_editor.getSession().setMode("ace/mode/css");
css_editor.setShowPrintMargin(false);

// PHP editor
var php_editor = ace.edit("php-editor");
php_editor.setTheme("ace/theme/monokai");
php_editor.getSession().setMode("ace/mode/php");
php_editor.setShowPrintMargin(false);