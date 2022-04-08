include .env

build:; 
	docker-compose build

run-local:;
	docker-compose up -d
stop-local:;
	docker-compose down

auth-ecr:;
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com
push-backend-image:;
	docker tag lasttime_api:latest $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com/lasttime-app/backend:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com/lasttime-app/backend:latest

deploy-cfn-stack:;
	aws cloudformation deploy --template-file ./aws/cloudformation/backend-template.yaml --stack-name $(STACK_NAME)-backend --capabilities CAPABILITY_IAM
	aws cloudformation deploy --template-file ./aws/cloudformation/frontend-template.yaml --stack-name $(STACK_NAME)-frontend

BACKEND_URL = https://`aws cloudformation describe-stacks --stack-name $(STACK_NAME)-backend | jq -r '.Stacks[].Outputs[].OutputValue'`
S3_BUCKET = s3://`aws cloudformation describe-stacks --stack-name $(STACK_NAME)-frontend | jq -r '.Stacks[].Outputs[] | select(.OutputKey == "FrontendBucketName") | .OutputValue'`
deploy-frontend-files:;
	rm -rf frontend/build
	cp -r frontend/src frontend/build
	sed -i -e "s|\$$BACKEND_URL|$(BACKEND_URL)|g" frontend/build/assets/js/app.js
	aws s3 sync frontend/build $(S3_BUCKET)