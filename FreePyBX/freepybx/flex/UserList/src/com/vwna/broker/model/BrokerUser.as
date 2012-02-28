package com.vwna.broker.model
{
	import mx.collections.ArrayCollection;
	
	[Bindable]
	public class BrokerUser 
	{
		public static var ALIAS		: String = 'com.vwna.broker.model.BrokerUser';
		
		public var name			: String;
		public var id		    : int;
		public var company_id	: int;
		public var sid			: String;
		public var email		: String;
		public var mobile		: String;
		public var ext			: String;
		public var uuid			: String;
		public var is_online    : Boolean;
		
		
	}
}