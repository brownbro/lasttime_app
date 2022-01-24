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
	aws cloudformation deploy --template-file ./aws/cloudformation/template.yaml --stack-name $(STACK_NAME) --capabilities CAPABILITY_IAM
