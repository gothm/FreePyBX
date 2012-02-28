//<![CDATA[

var paneId = 1;

function checkClose(pane, tab) {
    return confirm("Are you sure you want to lose your changes?");
}

var numMails;
var folder = 'INBOX';

var updateFetchStatus = function(x) {
    if (x == 0) {
        dijit.byId("fakeFetch").update({indeterminate:false});
        return;
    }

    dijit.byId("fakeFetch").update({progress:x + 1});
    if (x == numMails) {
        dojo.fadeOut({node:"fetchMail",duration:800,onEnd:function() {
            dijit.byId("fakeFetch").update({indeterminate:true});
            dojo.byId("fetchMail").style.visibility = "hidden";
        }}).play();
    }
};

var fakeReport = function(_num) {
    return dojo.string.substitute("Fetching: ${0} of ${1} messages.", [_num * this.maximum,this.maximum]);
};

var fakeDownload = function() {
    dojo.byId("fetchMail").style.visibility = "visible";
    numMails = Math.floor(Math.random() * 10) + 1;
    dijit.byId("fakeFetch").update({maximum:numMails,progress:0});
    dojo.fadeIn({node:"fetchMail",duration:300}).play();
    for (var ii = 0; ii < numMails + 1; ++ii) {
        var func = dojo.partial(updateFetchStatus, ii);
        setTimeout(func, ((ii + 1) * (Math.floor(Math.random() * 100) + 400)));
    }
};

var stopSendBar = function() {
    dijit.byId("sendMail").update({indeterminate:false});
    dijit.byId("sendDialog").hide();

    tabs.selectChild(dijit.byId("foldersTab"));
};

var showSendBar = function() {
    dijit.byId("sendMail").update({indeterminate:true});
    dijit.byId("sendDialog").show();
};

var formatDate = function(_date) {
    return dojo.date.locale.format(dojo.date.stamp.fromISOString(_date), {selector:"date"});
};

function getIconClassFolders(item, opened) {
    if (item.folder_name == "Trash")
        return "mailIconTrashcanFull";
    else if (item.folder_name == "Drafts")
        return "mailIconFolderDocuments";
    else if (item.folder_name == "INBOX")
        return "mailIconFolderInbox";
    else
        return "mailIconMailbox"
}

function genIndex() {
    var ci = dojo.byId("contactIndex");

    function setContacts(c, func, cls) {
        var span = document.createElement("span");
        span.innerHTML = c;
        span.className = cls || "contactIndex";
        ci.appendChild(span);
        new dojox.widget.FisheyeLite({
                    properties:{fontSize:1.5},
                    easeIn:dojo.fx.easing.linear,
                    durationIn:100,
                    easeOut:dojo.fx.easing.linear,
                    durationOut:100}, span);
        dojo.connect(span, "onclick", func || function() {
            contactTable.setQuery({first_name:c + "*"}, {ignoreCase:true});
        });
        dojo.connect(span, "onclick", function() {
            dojo.query(">", ci).removeClass("contactIndexSelected");
            dojo.addClass(span, "contactIndexSelected");
        });
    }

    setContacts("ALL", function() {
        contactTable.setQuery({});
    }, "contactIndexAll");
    for (var l = "A".charCodeAt(0); l <= "Z".charCodeAt(0); l++) {
        setContacts(String.fromCharCode(l));
    }
    setContacts("ALL", function() {
        contactTable.setQuery({});
    }, "contactIndexAll");
}

function searchMessages() {
    var term = {};
    var field = searchForm.attr("value");
    for (var key in field) {
        var val = field[key];
        if (val) {
            term[key] = "*" + val + "*";
        }
        headersGrid.setQuery(term, {ignoreCase:true});
    }
}

function getStore(_folder) {
    folder = _folder;

    dojo.xhrGet({
        url: "/api/get_message_headers/" + folder + "/",
        handleAs: "json",
        load: function(response, ioArgs) {
            var dataStore = new dojo.data.ItemFileReadStore({data: response, id:"headerStore"});
            var grid = dijit.byId("headersGrid").setStore(dataStore);
         },
         error : function(response, ioArgs) {
            alert("An error occurred while getting store for folder.");
         }
    });
}

function sendMessage(obj) {

    var output_msg = dojo.byId("output_message");
    var cform = dojo.byId("compose_form");

    showSendBar();

    dojo.xhrPost({
        url: "/api/send_message",
        handleAs: "text",
        form: cform,

        load: function(res) {
                alert(res);
                stopSendBar();
                cform.reset();
              },
        error: function(err, ioArgs) {
            alert(err);
            stopSendBar();
            cform.reset();

        }
    });

    var editor = dijit.byId("msg_editor");
    editor.attr("value", "");
}

dojo.require("dojox.html.entities");
dojo.addOnLoad(genIndex);

//]]>