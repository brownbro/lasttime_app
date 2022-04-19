include .env

init:;
	docker network create lasttime-app-local

build:; 
	docker-compose build
	cd backend/ && sam build --use-container

run-local:;
	docker-compose up -d
	cd backend/ && sam local start-api --docker-network lasttime-app-local
stop-local:;
	docker-compose down

create-frontend-stack:;
	aws cloudformation deploy --template-file ./aws/cloudformation/frontend-template.yaml --stack-name $(STACK_NAME)-frontend --parameter-overrides ACMCertificateArn=$(ACM_CERTIFICATE_ARN) DomainName=$(DOMAIN_NAME) HostedZoneId=$(HOSTED_ZONE_ID) BasicAuthBase64=$(BASIC_AUTH_BASE64)

deploy-backend:;
	cd backend/ && sam deploy

BACKEND_URL = `aws cloudformation describe-stacks --stack-name lasttime-app-stack-backend | jq -r '.Stacks[].Outputs[] | select(.OutputKey == "LasttimeAppbackendApi") | .OutputValue'`
S3_BUCKET = s3://`aws cloudformation describe-stacks --stack-name $(STACK_NAME)-frontend | jq -r '.Stacks[].Outputs[] | select(.OutputKey == "FrontendBucketName") | .OutputValue'`
deploy-frontend:;
	rm -rf frontend/build
	cp -r frontend/src frontend/build
	sed -i -e "s|\$$BACKEND_URL|$(BACKEND_URL)|g" frontend/build/assets/js/app.js
	aws s3 sync frontend/build $(S3_BUCKET)

delete-stacks:;
	aws cloudformation delete-stack --stack-name $(STACK_NAME)-frontend
	cd backend/ && sam delete