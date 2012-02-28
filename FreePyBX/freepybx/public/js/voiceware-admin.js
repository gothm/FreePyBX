/* 
 
    This Source Code Form is subject to the terms of the Mozilla Public 
    License, v. 2.0. If a copy of the MPL was not distributed with this 
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is PythonPBX/VoiceWARE.

    The Initial Developer of the Original Code is Noel Morgan, VoiceWARE, Inc.
    Copyright (c) 2011-2012 VoiceWARE, Inc. All Rights Reserved.
    
    http://www.vwna.com/ 
 
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
    dojo.require("dojox.form.uploader.plugins.Flash");    
    
    dojo.require("voiceware.notice.Notice");
    dojo.require("voiceware.notice.Error");
    dojo.require("voiceware.PbxForm");


    function reloadXML() {
        vwb.reloadXML();
        return false;
    }

    function reloadProfile(profile) {
        vwb.reloadProfile(profile);
        return false;
    }

    function reloadACL() {
        vwb.reloadACL();
        return false;
    }

    function showGateways(profile) {
        vwb.showGateways(profile);
        return false;
    }

    function sofiaStatus() {
        vwb.sofiaStatus();
        return false;
    }

    function showRegUsers(profile) {
        vwb.showRegUsers(profile);
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
    swfobject.embedSWF("/js/voiceware/flex/vwbroker/vwbroker.swf", "vwbroker", "10", "10", swfVersionStr, "expressInstall.swf", flashvars, params, attributes, function(e) { vwb = e.ref;});
});
