

dojo.provide("voiceware.PbxForm");

// Bring in what we need
dojo.require("dojo._base.declare");
dojo.require("dijit._Widget");
dojo.require("dijit._Templated");
dojo.require("dijit._WidgetsInTemplateMixin");
dojo.require("dijit.form.FilteringSelect");
dojo.require("dojo.data.ItemFileReadStore");
dojo.require("dijit._TemplatedMixin");
dojo.require("dijit.form.Form");
dojo.require("dijit.form.DateTextBox");
dojo.require("dojox.form.BusyButton");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.form.Button");
dojo.require("dojox.validate.web");
dojo.require("dojox.validate._base");
dojo.require("dijit.form.FilteringSelect");
dojo.require("dojo.data.ItemFileReadStore");


dojo.declare("voiceware.PbxForm", [dijit._Widget, dijit._Templated], {
    title: "",
    heading: "",
    legend: "",
    submitFunc: "",
    formName: "",
    helpCategory: "",
    delStyle: "",
    saveStyle: "",
    formNotice: "",
    noticeClass: "",
    templateString: dojo.cache("voiceware.PbxForm", "templates/PbxForm.html"),
    baseClass: "pbxForm",
    widgetsInTemplate: true
});
