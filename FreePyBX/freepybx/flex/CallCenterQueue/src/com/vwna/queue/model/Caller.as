package com.vwna.queue.model
{
	import mx.collections.ArrayCollection;
	
	[Bindable]
	public class Caller 
	{
		public static var ALIAS		: String = 'com.vwna.queue.model.Caller';
		
		public var uuid			: String;
		public var dest		    : String;
		public var cid_num		: String;
		public var cid_name		: String;
		public var direction	: String;
		public var time_in_queue	: String;
		public var created		: String;
		public var status		: String;
		public var to_user		: String;
	}
}