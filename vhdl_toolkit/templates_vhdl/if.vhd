IF {{ cond }} THEN
	{% for s in statements %}{{s}};
	{%endfor%}
END IF