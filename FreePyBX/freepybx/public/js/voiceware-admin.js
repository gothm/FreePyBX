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


    function checkPasswordStrength(pwd) {
        // Borrowed from somewhere, but forgot where :(
        // Needs Fixing...
        var strength_text = document.getElementById('strength_text');
        var strength_id = document.getElementById('strength_id');
        var progress_bar = document.getElementById('progress_bar');

        var strong = new RegExp('^(?=.{8,})(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*\\W).*$', 'g');
        var medium = new RegExp('^(?=.{6,})(((?=.*[A-Z])(?=.*[a-z]))|((?=.*[A-Z])(?=.*[0-9]))|((?=.*[a-z])(?=.*[0-9]))).*$', 'g');
        var enough = new RegExp('(?=.{6,}).*', 'g');

        if (strength_text == null) {
            return;
        }

        strength_id.value = 0;

        var width = pwd.length * 10;

        if (pwd.length == 0) {
            strength_text.innerHTML = '&nbsp;';
            progress_bar.style.backgroundColor = '#FFFFFF';
        }
        else if (false == enough.test(pwd)) {
            strength_text.innerHTML = 'Too short';
            progress_bar.style.backgroundColor = '#DC143C';
        }
        else if (strong.test(pwd)) {
            strength_text.innerHTML = 'Strong';
            width = 100;
            progress_bar.style.backgroundColor = '#228B22';
            strength_id.value = 3;
        }
        else if (medium.test(pwd)) {
            strength_text.innerHTML = 'Medium';
            width = 70;
            progress_bar.style.backgroundColor = '#FF8C30';
            strength_id.value = 2;
        }
        else {
            width = 60;
            strength_text.innerHTML = 'Weak';
            progress_bar.style.backgroundColor = '#FFD700';
            strength_id.value = 1;
        }

        progress_bar.style.width = width + '%';

        dojo.byId('password_strength').style.display = (pwd.length == 0) ? 'none' : '';
    }

    function reloadCallCenter() {
        vwb.reloadCallCenter();
        return false;
    }

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
    swfobject.embedSWF("/flash/vwbroker.swf", "vwbroker", "10", "10", swfVersionStr, "expressInstall.swf", flashvars, params, attributes, function(e) { vwb = e.ref;});
});
