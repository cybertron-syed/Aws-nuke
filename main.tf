module "aws-nuke" {
  source                         = "./modules"
  cloudwatch_schedule_expression = "cron(0 00 ? * FRI *)"
  older_than                     = "0d"
  aws_regions                    = ["ap-south-1"]
  include_resources              = "efs"
  exclude_resources              = null
  required_tags                  = "env=develop"
}
