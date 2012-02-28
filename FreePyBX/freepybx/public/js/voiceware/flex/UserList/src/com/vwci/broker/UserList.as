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

package com.vwci.broker
{
	import com.vwci.broker.model.*;
	import flash.display.DisplayObject;
	import flash.events.*;
	import flash.external.*;
	import flash.net.registerClassAlias;
	import flash.utils.*;
	import mx.charts.chartClasses.ChartBase;
	import mx.collections.*;
	import mx.collections.ArrayCollection;
	import mx.controls.Alert;
	import mx.controls.DataGrid;
	import mx.core.FlexGlobals;
	import mx.events.*;
	import mx.events.FlexEvent;
	import mx.managers.PopUpManager;
	import mx.messaging.ChannelSet;
	import mx.messaging.channels.SecureAMFChannel;
	import mx.rpc.AbstractOperation;
	import mx.rpc.events.FaultEvent;
	import mx.rpc.events.ResultEvent;
	import mx.rpc.remoting.mxml.RemoteObject;
	import spark.components.Application;
	import spark.components.List;
	import spark.components.TextInput;
	
	public class UserList extends Application
	{
		[Bindable]
		protected var users	: ArrayCollection;		
		
		public var lstUsers : List;
		public var timer:Timer = new Timer(10000);	
		[Bindable] public var sid:String = new String;	
		[Bindable] public var my_name:String;
		[Bindable] public var user_id:String = new String;	
		[Bindable] public var email:String = new String;	
		[Bindable] public var murl:String = new String;	
		
		public var chatSessions:ArrayCollection;
		
		public var isConnected:Boolean = false;			

		public function outboundIM(value:String):void {
	
		}
		
		public function UserList()
		{
			super();
			
			registerClassAlias(BrokerUser.ALIAS, BrokerUser);			
			addEventListener(FlexEvent.CREATION_COMPLETE, creationCompleteHandler);
		}		
		
		protected function creationCompleteHandler(event:FlexEvent):void
		{
			my_name = FlexGlobals.topLevelApplication.parameters.my_name;
			sid = FlexGlobals.topLevelApplication.parameters.sid;
			user_id = FlexGlobals.topLevelApplication.parameters.user_id;
			murl = FlexGlobals.topLevelApplication.parameters.murl;
			startTimer();			
			loadUsers();
		}
		
		public function startTimer():void {
			timer.addEventListener(TimerEvent.TIMER, onTimer);				
			timer.start(); 	
		}			

		private function onTimer(event:TimerEvent):void {
			pollWebService();
		}	
		
		public function callExtension(ext:String):void {
			var remoteObj:RemoteObject = getService();
			var operation:AbstractOperation = remoteObj.getOperation('callExtension');
			operation.send(FlexGlobals.topLevelApplication.parameters.sid, ext);
		}
		
		public function callMobile(mobile:String):void {		
			var remoteObj:RemoteObject = getService();
			var operation:AbstractOperation = remoteObj.getOperation('callMobile');
			operation.send(FlexGlobals.topLevelApplication.parameters.sid, mobile);			
		}	

		private function pollWebService():void {
			loadUsers();
		}				
		
		/**
		 * Load list of persistent users from server.
		 */
		public function loadUsers(event:FlexEvent=null):void
		{
			var remoteObj:RemoteObject = getService();
			var operation:AbstractOperation = remoteObj.getOperation('getUsers');
			operation.addEventListener(ResultEvent.RESULT, getUsers_resultHandler);
			operation.send(FlexGlobals.topLevelApplication.parameters.sid);
		}
		
		protected function getUsers_resultHandler(event:ResultEvent):void
		{
			enabled = true;
			event.target.removeEventListener(ResultEvent.RESULT, getUsers_resultHandler);
			users = ArrayCollection(ResultEvent(event).result);
		}
		
		/**
		 * Create a RemoteObject with url from user input.
		 */
		
		public function getService():RemoteObject
		{
			var surl:String = 'https://'+murl+'/flash_gateway';
			var channel:SecureAMFChannel = new SecureAMFChannel("voiceware", surl);
			
			var channels:ChannelSet = new ChannelSet();
			channels.addChannel(channel);
			
			var remoteObject:RemoteObject = new RemoteObject("VoiceWareService");
			remoteObject.showBusyCursor = false;
			remoteObject.channelSet = channels;
			remoteObject.addEventListener(FaultEvent.FAULT, onServiceFault);
			
			return remoteObject;
		}
		
		/**
		 * Service reported an error.
		 *
		 * @param event Event containing error information.
		 */
		protected function onServiceFault(event:FaultEvent):void
		{
			// errorMsg:String = 'Service error: ' + event.fault.faultCode;
			//Alert.show(event.fault.faultDetail, errorMsg);
			ExternalInterface.call("logout", event.fault.faultCode);
		}
		
	}
}