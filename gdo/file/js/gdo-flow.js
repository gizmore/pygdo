"use strict";

/* Upload a GDT_File immediately and keep it in the session until the normal
 * form submission validates and persists it. Native FormData avoids coupling
 * PyGDO to the unrelated legacy npm package named "flow.js". */
document.querySelectorAll('.gdo-flow-file input[type=file], input[type=file].gdo-flow-file').forEach(function(input) {
	const target = new URL(window.location.href);
	target.pathname = target.pathname.replace(/\.html$/, '.json');
	target.searchParams.set('flowField', input.name);

	function setLoading(loading) {
		const loadingPane = document.getElementById('gdt-loading-pane');
		if (loadingPane) {
			loadingPane.classList.toggle('done', !loading);
		}
	}

	function showSuccess(file) {
		const label = document.getElementById('gdo-file-input-' + input.name);
		if (label) {
			label.textContent = file.file.name + ' (' + file.file.size + ' bytes)';
		}

		const preview = document.getElementById('gdo-file-preview-' + input.name);
		if (preview && file.file.type && file.file.type.startsWith('image/')) {
			const image = document.createElement('img');
			image.className = 'gdo-file-preview';
			image.alt = file.file.name;
			preview.appendChild(image);
			const reader = new FileReader();
			reader.onload = function(event) {
				image.src = event.target.result;
			};
			reader.readAsDataURL(file.file);
		}
	}

	function showError(file, message) {
		console.error('PyGDO file upload failed:', message);
		const label = document.getElementById('gdo-file-input-' + input.name);
		if (label) {
			label.textContent = 'Upload failed: ' + file.file.name;
		}
	}

	input.addEventListener('change', function() {
		const file = input.files[0];
		if (!file) {
			return;
		}
		const form = new FormData();
		form.append(input.name, file, file.name);
		input.disabled = true;
		setLoading(true);
		fetch(target, {
			method: 'POST',
			body: form,
			credentials: 'same-origin',
		})
		.then(function(response) {
			if (!response.ok) {
				throw new Error('HTTP ' + response.status);
			}
			return response.json();
		})
		.then(function(response) {
			if (!response || response.code !== 200 || !response.data || response.data.result !== 'success') {
				throw new Error('Unexpected upload response');
			}
			showSuccess({file: file});
		})
		.catch(function(error) {
			showError({file: file}, error);
		})
		.finally(function() {
			input.disabled = false;
			setLoading(false);
		});
	});
});
