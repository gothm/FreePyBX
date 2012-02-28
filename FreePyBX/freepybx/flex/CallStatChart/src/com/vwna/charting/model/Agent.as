package com.vwna.charting.model
{
	import mx.collections.ArrayCollection;
	
	[Bindable]
	public class Agent 
	{
		public static var ALIAS		: String = 'com.vwna.charting.model.Agent';
		
		public var agent_name		: String;
		public var volume		    : int;
		public var talk_time		: int;

	}
}