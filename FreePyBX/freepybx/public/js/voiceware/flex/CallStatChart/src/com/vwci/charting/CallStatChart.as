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


package com.vwci.charting
{
	import com.vwci.charting.model.Agent;
	
	import flash.display.DisplayObject;
	import flash.net.registerClassAlias;
	
	import mx.charts.chartClasses.ChartBase;
	import mx.collections.ArrayCollection;
	import mx.controls.Alert;
	import mx.controls.DataGrid;
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
	import spark.components.TextInput;
	import mx.core.FlexGlobals;
	
	public class CallStatChart extends Application
	{
		[Bindable]
		protected var agents	: ArrayCollection;
		[Bindable] public var murl:String = new String;
		
//		public var server		: TextInput;
//		public var port			: TextInput;
		public var agentChart : ChartBase;
		
		/**
		 * Constructor.
		 */
		public function CallStatChart()
		{
			super();
			
			// These mappings must use the same aliases defined with the PyAMF
			// function 'pyamf.register_class'.
			registerClassAlias(Agent.ALIAS, Agent);			
			addEventListener(FlexEvent.CREATION_COMPLETE, creationCompleteHandler);
		}
		
		protected function creationCompleteHandler(event:FlexEvent):void
		{
			murl = FlexGlobals.topLevelApplication.parameters.url;
			loadAgents();
		}
		
		
		/**
		 * Load list of persistent users from server.
		 */
		public function loadAgents(event:FlexEvent=null):void
		{
			var remoteObj:RemoteObject = getService();
			var operation:AbstractOperation = remoteObj.getOperation('getAgents');
			operation.addEventListener(ResultEvent.RESULT, getAgents_resultHandler);
			operation.send(FlexGlobals.topLevelApplication.parameters.sid);
		}
		
		protected function getAgents_resultHandler(event:ResultEvent):void
		{
			enabled = true;
			event.target.removeEventListener(ResultEvent.RESULT, getAgents_resultHandler);
			agents = ArrayCollection(ResultEvent(event).result);
		}
		
		/**
		 * Create a RemoteObject with url from user input.
		 */
		
		public function getService():RemoteObject
		{			
			var url:String = 'https://'+murl+'/flash_gateway';
			var channel:SecureAMFChannel = new SecureAMFChannel("voiceware", url);
			
			// Create a channel set and add your channel(s) to it
			var channels:ChannelSet = new ChannelSet();
			channels.addChannel(channel);
			
			// Create a new remote object and set channels
			var remoteObject:RemoteObject = new RemoteObject("VoiceWareService");
			remoteObject.showBusyCursor = true;
			remoteObject.channelSet = channels;
			remoteObject.addEventListener(FaultEvent.FAULT, onServiceFault);
			
			return remoteObject;
		}
		
//		/**
//		 * Edit a user record.
//		 */
//		protected function editUser():void
//		{
//			if (userGrid.selectedItem == null)
//			{
//				return;
//			}
//			
//			var dlg:EditUserDlg = new EditUserDlg();
//			dlg.user = User(userGrid.selectedItem);
//			PopUpManager.addPopUp(dlg, DisplayObject(this), true);
//		}
//		
//		/**
//		 * Add a new user.
//		 */
//		protected function addUser():void
//		{
//			var user:User = new User();
//			var dlg:EditUserDlg = new EditUserDlg();
//			dlg.user = user;
//			PopUpManager.addPopUp(dlg, DisplayObject(this), true);
//		}
//		
//		/**
//		 * Remove an existing user.
//		 */
//		protected function removeUser():void
//		{
//			if (userGrid.selectedItems == null || userGrid.selectedItems.length < 1)
//			{
//				return;
//			}
//			
//			var removeKeys:Array = [];
//			for each (var item:Object in userGrid.selectedItems)
//			{
//				removeKeys.push(item.sa_key);
//			}
//			
//			var remoteObj:RemoteObject = getService();
//			var operation:AbstractOperation = remoteObj.getOperation('removeList');
//			operation.addEventListener(ResultEvent.RESULT, remove_resultHandler);
//			operation.send(User.ALIAS, removeKeys);
//		}
//		
//		protected function remove_resultHandler(event:Event):void
//		{
//			event.target.removeEventListener(ResultEvent.RESULT, remove_resultHandler);
//			loadAgents();
//		}
		
		/**
		 * Service reported an error.
		 *
		 * @param event Event containing error information.
		 */
		protected function onServiceFault(event:FaultEvent):void
		{
			var errorMsg:String = 'Service error: ' + event.fault.faultCode;
			Alert.show(event.fault.faultDetail, errorMsg);
		}
		
	}
}