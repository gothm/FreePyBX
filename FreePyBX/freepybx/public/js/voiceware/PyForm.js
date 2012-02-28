

dojo.provide("voiceware.PyForm");

// Bring in what we need
dojo.require("dojo._base.declare");
dojo.require("dijit._Widget");
dojo.require("dijit._Templated");
dojo.require("dijit._WidgetsInTemplateMixin");
dojo.require("dijit.form.FilteringSelect");
dojo.require("dojo.data.ItemFileReadStore");
dojo.require("dijit.form.Form");
dojo.require("dijit.form.DateTextBox");
dojo.require("dojox.form.BusyButton");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.form.Button");
dojo.require("dojox.validate.web");
dojo.require("dojox.validate._base");
dojo.require("dijit.form.FilteringSelect");
dojo.require("dojo.data.ItemFileReadStore");



// Declare Dojo widget name. This widget extends the Label widget
dojo.declare("voiceware.PyForm", [dijit._Widget, dijit._Templated], {
            heading: "",
            legend: "",
            submitFunc: "",
            formName: "",
            helpCategory: "",
            delStyle: "",
            saveStyle: "",
            formNotice: "",
            noticeClass: "",
            templateString: dojo.cache("voiceware.PyForm", "templates/PyForm.html"),
            baseClass: "pyForm",
            widgetsInTemplate: true

//            constructor: function(obj) {
//                this.heading = obj.heading;
//                this.html_content = obj.html_content;
//                this.top_buttons = obj.top_buttons;
//                this.bottom_buttons = obj.bottom_buttons;
//                this.legend = obj.legend;
//                this.submitFunc = obj.submitFunc;
//                this.form_name = obj.form_name;
//                this.help_category = obj.help_category;
//                this.deleteFunc = obj.deleteFunc;
//            },


//
//            postCreate: function(){
//                // Get a DOM node reference for the root of our widget
//                var domNode = this.domNode;
//
//                // Run any parent postCreate processes - can be done at any point
//                this.inherited(arguments);
//
//                // Set up our mouseenter/leave events - using dijit/_WidgetBase's connect
//                // means that our callback will execute with `this` set to our widget
//                this.connect(domNode, "onmouseenter", function(e) {
//                    //this._changeBackground(this.mouseBackgroundColor);
//                });
//                this.connect(domNode, "onmouseleave", function(e) {
//                    //this._changeBackground(this.baseBackgroundColor);
//                });
//            }
//

//            postMixInProperties: function(){
//                if (dijit.byId(this.id)) {
//                    dijit.byId(this.id).destroyRecursive();
//                }
//            },
//
//            destroyRecursive: function(){
//                dojo.forEach(this.getDescendants(), function(widget){
//                    widget.destroyRecursive();
//                });
//                this.inherited(arguments);
//            }

        });
