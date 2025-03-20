provider "aws" {
  region = "us-east-1"
}
resource "aws_db_instance" "license_plate_db" {
  identifier         = "license-plate-db"
  engine             = "postgres"
  instance_class     = "db.t2.micro"
  allocated_storage   = 20
  username           = var.db_user
  password           = var.db_password
  db_name            = var.db_name
  skip_final_snapshot = true
}
resource "aws_lambda_function" "process_license_plate" {
  function_name = "process_license_plate"
  handler       = "handler.process_license_plate"
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_exec.arn
  filename      = "path/deployment/package.zip" 
  environment {
    DB_HOST     = aws_db_instance.license_plate_db.address
    DB_USER     = var.db_user
    DB_PASSWORD = var.db_password
    DB_NAME     = var.db_name
  }
}
resource "aws_lambda_function" "get_metrics" {
  function_name = "get_metrics"
  handler       = "handler.get_metrics"
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_exec.arn
  filename      = "path/deployment/package.zip" 
  environment {
    DB_HOST     = aws_db_instance.license_plate_db.address
    DB_USER     = var.db_user
    DB_PASSWORD = var.db_password
    DB_NAME     = var.db_name
  }
}
resource "aws_api_gateway_rest_api" "api" {
  name        = "LicensePlateAPI"
  description = "API para procesar lecturas de patentes"
}
resource "aws_api_gateway_resource" "process" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "process"
}
resource "aws_api_gateway_resource" "metrics" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "metrics"
}
resource "aws_api_gateway_method" "post_process" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.process.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "get_metrics" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.metrics.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "process_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.process.id
  http_method             = aws_api_gateway_method.post_process.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.process_license_plate.invoke_arn
}
resource "aws_api_gateway_integration" "metrics_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.metrics.id
  http_method             = aws_api_gateway_method.get_metrics.http_method
  integration_http_method = "GET"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_metrics.invoke_arn
}
resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_license_plate.function_name
  principal     = "apigateway.amazonaws.com"
}
resource "aws_lambda_permission" "allow_api_gateway_metrics" {
  statement_id  = "AllowAPIGatewayInvokeMetrics"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_metrics.function_name
  principal     = "apigateway.amazonaws.com"
}
output "api_endpoint" {
  value = "${aws_api_gateway_rest_api.api.invoke_url}/process"
}
output "metrics_endpoint" {
  value = "${aws_api_gateway_rest_api.api.invoke_url}/metrics"
}