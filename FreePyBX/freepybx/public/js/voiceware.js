/* 
 
    This Source Code Form is subject to the terms of the Mozilla Public 
    License, v. 2.0. If a copy of the MPL was not distributed with this 
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is FreePyBX/VoiceWARE.

    The Initial Developer of the Original Code is Noel Morgan, VoiceWARE, Inc.
    Copyright (c) 2011-2012 VoiceWARE, Inc. All Rights Reserved.
    
    http://www.vwci.com/
 */
    dojo.require("dojo.parser");
    dojo.require("dojo.data.ItemFileWriteStore");
    dojo.require("dojo.data.ItemFileReadStore");    
    
    dojo.require("dijit.Tree");
    dojo.require("dijit.Editor");
    dojo.require('dijit.form.Form');
    dojo.require("dijit._Widget");
    dojo.require("dijit.form.TextBox");
    dojo.require("dijit.Toolbar");
    dojo.require("dijit.ProgressBar");
    dojo.require("dijit.form.CheckBox");
    dojo.require("dijit.form.Button");
    dojo.require("dijit.Dialog");
    dojo.require("dijit.Declaration");
    dojo.require('dijit.form.FilteringSelect');
    dojo.require('dijit.form.ValidationTextBox');
    dojo.require('dijit.form.DateTextBox');
    dojo.require('dijit.form.TimeTextBox');
    dojo.require('dijit.form.Button');
    dojo.require('dijit.form.RadioButton');    
    dojo.require("dijit.layout.BorderContainer");
    dojo.require("dijit.layout.TabContainer");
    dojo.require("dijit.layout.ContentPane");    
    dojo.require("dijit.layout.AccordionContainer");    
    dojo.require("dijit._editor.plugins.FontChoice");
    dojo.require("dijit._editor.plugins.LinkDialog");
    dojo.require("dijit.tree.dndSource");
    dojo.require("dijit.form.ComboBox");    
    dojo.require("dijit.Menu");
    dojo.require("dijit.MenuItem");
    dojo.require("dijit.MenuSeparator");
    dojo.require("dijit.PopupMenuItem");
    dojo.require("dijit.ColorPalette");
   
    dojo.require('dojox.validate');
    dojo.require('dojox.validate.us');
    dojo.require('dojox.validate.web');
    dojo.require('dojox.form.BusyButton');    
    dojo.require('dojox.form.CheckedMultiSelect');
    dojo.require("dojox.layout.ContentPane");
    dojo.require("dojox.grid.DataGrid");
    dojo.require("dojox.widget.FisheyeLite");
    dojo.require("dojox.grid.EnhancedGrid");
    dojo.require("dojox.grid.enhanced.plugins.DnD");
    dojo.require("dojox.grid.enhanced.plugins.Menu");
    dojo.require("dojox.grid.enhanced.plugins.NestedSorting");
    dojo.require("dojox.grid.enhanced.plugins.IndirectSelection");    
    dojo.require("dojox.html.entities");
    dojo.require("dijit.form.Textarea");
    
    dojo.require("dojox.grid.enhanced.plugins.Menu");
    dojo.require("dojo.data.ItemFileWriteStore");
    dojo.require("dojox.grid.enhanced.plugins.Pagination");
    dojo.require("dojox.grid.enhanced.plugins.Filter");        
    
    dojo.require("dijit.dijit");
    dojo.require("dojox.widget.Portlet");
    dojo.require("dojox.widget.FeedPortlet");
    dojo.require("dojox.layout.GridContainer");
    dojo.require("dojox.widget.Calendar");    
    
    dojo.require("dojox.form.Uploader");
    dojo.require("dojox.form.uploader.FileList"); 
    
    dojo.require("voiceware.notice.Notice");
    dojo.require("voiceware.notice.Error");      
    dojo.require("dojox.image.Lightbox");
    dojo.require("dojox.widget.DialogSimple");
    dojo.require("voiceware.PbxForm");
   

    function showCallerPop(data) {
        dijit.byId("dlgNotice").set("content", data.message);
        dijit.byId("dlgNotice").set("title", data.caller);
        dijit.byId("dlgNotice").show();
        return true;
    }

    function extNotice(data) {
        new voiceware.notice.Notice({message: data});
        return true;
    }

    function callFlow(data) {        
        document.getElementById("call_route_from").innerHTML = data.cid_num;
        document.getElementById("route_uuid").value = data.uuid;
        dijit.byId("dlgRouteCall").show();
        return true;
    }        

    function getCallQueueRecordings(queue) {
        tmpObj = queue;
        dijit.byId("callCenterContent").set("href", "/cc_queue_recordings.html");
    }
    
    function getCampaignLeads(campaign) {
        tmpObj = campaign;
        dijit.byId("crmContent").set("href", "/crm_campaign_leads.html");
    }    
    
    function logout(obj) {
         document.location.href = "/logout";
         return;
    }
    
    function selectTab(bc,pn,href) {
        var tabs = dijit.byId("tabs");
        var bc = dijit.byId(bc);
        dijit.byId(pn).set("href", href);
        tabs.selectChild(bc);       
    }

    function showFax(img) {
        myWindow=window.open(img,'Fax Received','toolbar=yes,location=no,width=600,height=800');
    }

    function checkPasswordStrength(pwd) {
        // Borrowed from somewhere, but forgot where :(
        // Needs Fixing...
        var strength_text = document.getElementById('strength_text');
        var strength_id = document.getElementById('strength_id');
        var progress_bar = document.getElementById('progress_bar');

        var strong = new RegExp('^(?=.{8,})(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*\\W).*$', 'g');
        var medium = new RegExp('^(?=.{6,})(((?=.*[A-Z])(?=.*[a-z]))|((?=.*[A-Z])(?=.*[0-9]))|((?=.*[a-z])(?=.*[0-9]))).*$', 'g');
        var enough = new RegExp('(?=.{6,}).*', 'g');

        if (strength_text == null)
        {
            return;
        }

        strength_id.value = 0;

        var width = pwd.length * 10;

        if (pwd.length == 0)
        {
            strength_text.innerHTML = '&nbsp;';
            progress_bar.style.backgroundColor = '#FFFFFF';
        }
        else if (false == enough.test(pwd))
        {
            strength_text.innerHTML = 'Too short';
            progress_bar.style.backgroundColor = '#DC143C';
        }
        else if (strong.test(pwd))
        {
            strength_text.innerHTML = 'Strong';
            width = 100;
            progress_bar.style.backgroundColor = '#228B22';
            strength_id.value = 3;
        }
        else if (medium.test(pwd))
        {
            strength_text.innerHTML = 'Medium';
            width = 70;
            progress_bar.style.backgroundColor = '#FF8C30';
            strength_id.value = 2;
        }
        else
        {
            width = 60;
            strength_text.innerHTML = 'Weak';
            progress_bar.style.backgroundColor = '#FFD700';
            strength_id.value = 1;
        }

        progress_bar.style.width = width + '%';

        document.getElementById('password_strength').style.display = (pwd.length == 0)?'none':'';
    }

    
    function userEditFormHandler() {
        var output_msg = dojo.byId("output_message");

        dojo.xhrPost({
            url: "/crm/edit_user",
            handleAs: "text",
            form: dojo.byId("user_edit_form"),
            load: function(res) {
                if (res.indexOf("Error") == -1) {
                    new voiceware.notice.Notice({message: "User successfully updated."});
                } else {
                    new voiceware.notice.Error({message: res});
                }
                 return res;
            },
            error: function(err, ioArgs) {
                new voiceware.notice.Error({message: err});
                return err;
            }
        });
    }
    
    function myLabelFunc(item, store) {
        var label = store.getValue(item, 'name');
        //label=label.substr(0, label.length-1);
        label = label.toLowerCase();
        return label;
    }    
    
    itemToJS = function(store, item) {
        var js = {};
            if (item && store) {
                var attributes = store.getAttributes(item);
                if (attributes && attributes.length > 0) {
                    var i;
                    for (i = 0; i < attributes.length; i++) {
                        var values = store.getValues(item, attributes[i]);
                        if (values) {
                            if (values.length > 1) {
                                var j;
                                js[attributes
                                    [i]] = [];
                                for (j = 0; j < values.length; j++) {
                                    var value = values[j];
                                    if (store.isItem(value)) {
                                        js[attributes
                                            [i]].push(itemToJS(store, value));
                                    } else {
                                        js[attributes
                                            [i]].push(value);
                                    }
                                }
                            } else { if (store.isItem(values[0])) {
                                js[attributes
                                    [i]] = itemToJS(store, values[0]);
                            } else {
                                js[attributes
                                    [i]] = values[0];
                            }
                        }
                    }
                }
            }
        }
        return js;
    };

    
    Date.prototype.json = function(){ return dojo.date.stamp.toISOString(this, {selector: 'date'});};
    
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
            url : "/pymp/get_message_headers/" + folder + "/",
            handleAs : "json",
            load : function(response, ioArgs) {
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
            url: "/pymp/send_message",
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

    function showHelp(id) {
        dijit.byId("help_dlg").set("href", "/help/"+id+".html");
        dijit.byId("help_dlg").set("title", "FreeGUIPy Help");
        dijit.byId("help_dlg").show();
        return true;
    }

    function brokerMessage(msg) {
        dijit.byId("help_dlg").set("content", msg);
        dijit.byId("help_dlg").set("title", "Broker Message");
        dijit.byId("help_dlg").set("style", "width: 400px; height: 400px;");
        dijit.byId("help_dlg").show();
        return true;
    }

    function routeCall() {
        vwb.routeCall(document.getElementById("route_uuid").value+':'+document.getElementById("call_route_to").value);
        dijit.byId("dlgRouteCall").hide();
        return;
    }

    function callNumber(num) {
        vwb.callNumber(num);
        return;
    }

    function reloadCallCenter() {
        vwb.reloadCallCenter();
        return false;
    }


dojo.ready(function() {
    var swfVersionStr = "10.0.0";
    var xiSwfUrlStr = "";
    var flashvars = {};
    flashvars.sid = sid;
    flashvars.my_name = my_name;
    flashvars.user_id = uid;
    flashvars.murl = location.hostname;
    var params = {};
    params.quality = "high";
    params.bgcolor = "#13395e";
    params.allowscriptaccess = "always";
    params.allownetworking = "all"
    var attributes = {};
    attributes.id = "vw_broker";
    attributes.name = "vw_broker";
    attributes.align = "middle";
    swfobject.embedSWF("/flash/vwbroker.swf", "vwbroker", "10", "10", swfVersionStr, "expressInstall.swf", flashvars, params, attributes, function(e) { vwb = e.ref;});
});