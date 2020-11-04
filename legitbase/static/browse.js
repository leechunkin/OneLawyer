'use strict';

document.addEventListener('DOMContentLoaded', function () {
	var stack, lang, container, subcategories, selects, ready, browse;
	stack = [];
	lang = document.documentElement.getAttribute('lang');
	container = document.getElementById('categories');
	subcategories = container.children;
	selects = container.getElementsByTagName('select');
	ready = document.getElementsByClassName('ready');
	browse = document.getElementById('browse');

	function add_categories(nodes, preselected) {
		function get_preselected_index() {
			var id, node, index;
			id = preselected ? preselected.shift() : undefined;
			index = id ? nodes.findIndex(function (e) {return e.id === id}) : -1;
			return Math.max(0, index);
		}

		var level, i, select, option, text;
		level = stack.length;
		select = selects[level];
		while (select.firstChild) select.removeChild(select.firstChild);
		option = document.createElement('option');
		option.value = -1;
		option.setAttribute('disabled', '');
		switch (lang) {
			case 'zh':
				text = '請選擇服務';
				break;
			case 'en':
				text = 'Select service here';
				break;
		}
		option.appendChild(document.createTextNode(text));
		select.appendChild(option);
		for (i=0; i<nodes.length; ++i) {
			option = document.createElement('option');
			option.value = i;
			switch (lang) {
				case 'zh':
					text = nodes[i].data.name_zh;
					break;
				case 'en':
					text = nodes[i].data.name;
					break;
			}
			option.appendChild(document.createTextNode(text));
			select.appendChild(option);
		}
		select.selectedIndex = 0;
		stack.push(nodes);
		subcategories[level].hidden = false;
		if (preselected !== undefined)
			(function (selected) {
				if (nodes.length > selected) {
					select.selectedIndex = selected+1;
					return add_subcategories(nodes[selected], preselected);
				}
			})(get_preselected_index());
	}

	function add_subcategories(node, preselected) {
		var i;
		if ('children' in node) {
			for (i=0; i<ready.length; ++i)
				ready[i].hidden = true;
			return add_categories(node.children, preselected);
		} else {
			browse.form.action = '/' + lang + '/service/' + node.id + '/';
			for (i=0; i<ready.length; ++i)
				ready[i].removeAttribute('hidden');
		}
	}

	function filters_code() {
		var inputs, options, binary;
		var i;
		var table =
			'ABCDEFGHIJKLMNOPQRSTUVWXYZ' +
			'abcdefghijklmnopqrstuvwxyz' +
			'0123456789-_';
		inputs = browse.form.getElementsByTagName('input');
		options = [];
		for (i=0; i<inputs.length; ++i) {
			var input;
			input = inputs.item(i);
			if (input.name)
				options.push(
					{
						name: input.name,
						checked: !!input.checked
					}
				);
		}
		options = options.sort(
			function (a, b) {
				if (a.name < b.name)
					return -1;
				else if (a.name > b.name)
					return +1;
				else
					return 0;
			}
		);
		binary = [];
		for (i=0; i<options.length; ++i) {
			var c, b;
			c = Math.floor(i/6);
			b = i - c*6;
			if (c == 0) binary.push(0);
			if (options[i].checked) binary[c] |= 1 << b;
		}
		return binary.map(function (n) {return table[n]}).join('');
	}

	(function () {
		var i;
		for (i=0; i<selects.length; ++i)
			(function (level) {
				selects[i].addEventListener('change', function () {
					var j;
					for (j=level+1; j<subcategories.length; ++j)
						subcategories[j].setAttribute('hidden', '');
					stack.splice(level+1);
					if (this.value < 0) return;
					return add_subcategories(stack[level][this.value]);
				})
			})(i);
	})();
	browse.addEventListener('click', function () {
		var f, sort, s;
		f = '?f=' + filters_code();
		s =
			(function (sort) {
				return sort ? '&s=' + sort.value : '';
			})(document.getElementById('sort'));
		window.location.assign(browse.form.action + f + s);
	});

	if (typeof categories_chosen === 'undefined')
		add_categories(categories);
	else
		add_categories(categories, categories_chosen);
});
