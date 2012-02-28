/*
This Source Code Form is subject to the terms of the Mozilla Public 
License, v. 2.0. If a copy of the MPL was not distributed with this 
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Software distributed under the License is distributed on an "AS IS"
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
License for the specific language governing rights and limitations
under the License.

The Original Code is PythonPBX/VoiceWARE.

The Initial Developer of the Original Code is Noel Morgan, 
Copyright (c) 2011-2012 VoiceWARE Communications, Inc. All Rights Reserved.

http://www.vwci.com/ 

You may not remove or alter the substance of any license notices (including
copyright notices, patent notices, disclaimers of warranty, or limitations 
of liability) contained within the Source Code Form of the Covered Software, 
except that You may alter any license notices to the extent required to 
remedy known factual inaccuracies.  

*/

package com.vwci.broker.model
{
	
	[Bindable]
	[RemoteClass(alias="com.vwci.broker.model.Message")] 

	public class Message
	{
		public var name		: String;
		public var email 	: String;
		public var id		: int;
		public var message	: String;
		public var sid		: String;
		public var command  : String;
		public var data     : Object;
		
		
		public function Message(name:String="", email:String="", id:int=0,
								message:String="", sid:String="", command:String="")
		{
			this.name = name;
			this.email = email;
			this.id = id;
			this.message = message;
			this.sid = sid;
			this.command = command;
		}
		
	}
}    