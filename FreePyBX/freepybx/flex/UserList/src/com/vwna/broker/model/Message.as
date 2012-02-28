package com.vwna.broker.model
{
	
	[Bindable]
	[RemoteClass(alias="com.vwna.broker.model.Message")] 

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