package com.vwna.queue
{
	import com.vwna.queue.model.*;
	
	import flash.display.DisplayObject;
	import flash.events.*;
	import flash.external.*;
	import flash.net.registerClassAlias;
	import flash.utils.*;	
	import mx.charts.chartClasses.ChartBase;
	import mx.collections.*;
	import mx.collections.ArrayCollection;
	import mx.controls.Alert;
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
	import spark.components.DataGrid;
	import spark.components.List;
	import spark.components.TextInput;
	
	
	public class CallQueue extends Application
	{
		[Bindable]
		protected var callers	: ArrayCollection;		
		
		public var dgCallers : DataGrid;
		public var timer:Timer = new Timer(10000);	
		import flash.external.*;
		[Bindable] public var sid:String = new String;	
		[Bindable] public var my_name:String;
		[Bindable] public var user_id:String = new String;	
		[Bindable] public var email:String = new String;	
		[Bindable] public var murl:String = new String;
				
		/**
		 * Constructor.
		 */
		public function CallQueue()
		{
			super();
			
			registerClassAlias(Caller.ALIAS, Caller);			
			addEventListener(FlexEvent.CREATION_COMPLETE, creationCompleteHandler);
		}
		
		protected function creationCompleteHandler(event:FlexEvent):void
		{
			my_name = FlexGlobals.topLevelApplication.parameters.my_name;
			sid = FlexGlobals.topLevelApplication.parameters.sid;
			murl = FlexGlobals.topLevelApplication.parameters.murl;
			user_id = FlexGlobals.topLevelApplication.parameters.user_id;
			startTimer();			
			loadCallers();
		}
		
		public function startTimer():void {
			timer.addEventListener(TimerEvent.TIMER, onTimer);				
			timer.start(); 	
		}		

		private function onTimer(event:TimerEvent):void {
			pollWebService();
		}	
		
		private function pollWebService():void {
			loadCallers();
		}				
		
		/**
		 * Load list of persistent users from server.
		 */
		public function loadCallers(event:FlexEvent=null):void
		{
			var remoteObj:RemoteObject = getService();
			var operation:AbstractOperation = remoteObj.getOperation('getCallers');
			operation.addEventListener(ResultEvent.RESULT, getCallers_resultHandler);
			operation.send(FlexGlobals.topLevelApplication.parameters.sid);
		}
		
		protected function getCallers_resultHandler(event:ResultEvent):void
		{
			enabled = true;
			event.target.removeEventListener(ResultEvent.RESULT, getCallers_resultHandler);
			callers = ArrayCollection(ResultEvent(event).result);
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
			var errorMsg:String = 'Service error: ' + event.fault.faultCode;
			Alert.show(event.fault.faultDetail, errorMsg);
		}
		
	}
}