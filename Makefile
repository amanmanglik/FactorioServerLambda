zip: clean
	pushd .venv/lib/python3.8/site-packages; zip -r "../../../../dist/factorio_server_lambda.zip" . ;	popd

	zip -g dist/factorio_server_lambda.zip lambda_function.py


clean:
	rm -f dist/factorio_server_lambda.zip


upload: zip
	aws lambda update-function-code --function-name tarvis-factorio-server-manager-discord --zip-file fileb://dist/factorio_server_lambda.zip

virtenv:
	python3.8 -m venv .venv
	pip install -r requirements.txt
