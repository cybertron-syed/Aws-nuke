# -*- coding: utf-8 -*-

"""Module deleting all rds resources."""

import logging
import time

import boto3

from botocore.exceptions import ClientError, EndpointConnectionError


def nuke_all_rds(older_than_seconds):
    """Rds resources deleting function.

    Deleting all rds resources with
    a timestamp greater than older_than_seconds.
    That include:
      - Aurora clusters
      - rds instances
      - snapshots
      - subnets
      - param groups

    :param int older_than_seconds:
        The timestamp in seconds used from which the aws
        resource will be deleted
    """
    # Convert date in seconds
    time_delete = time.time() - older_than_seconds

    # define connection
    rds = boto3.client("rds")

    # Test if rds services is present in current aws region
    try:
        rds.describe_db_instances()
    except EndpointConnectionError:
        print("rds resource is not available in this aws region")
        return

    # List all rds instances
    rds_instance_list = rds_list_instances(time_delete)

    # Nuke all rds instances
    for instance in rds_instance_list:

        # Delete rds instance
        try:
            rds.delete_db_instance(DBInstanceIdentifier=instance)
            print("Stop rds instance {0}".format(instance))
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "InvalidDBInstanceState":
                logging.info("rds instance %s is not started", instance)
            else:
                logging.error("Unexpected error: %s", e)

    # List all rds clusters
    rds_cluster_list = rds_list_clusters(time_delete)

    # Nuke all rds clusters
    for cluster in rds_cluster_list:

        # Delete Aurora cluster
        try:
            rds.delete_db_cluster(DBClusterIdentifier=cluster)
            print("Nuke rds cluster {0}".format(cluster))
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "InvalidDBClusterStateFault":
                logging.info("rds cluster %s is not started", cluster)
            else:
                logging.error("Unexpected error: %s", e)


def rds_list_instances(time_delete):
    """Rds instance list function.

    List IDs of all rds instances with a timestamp
    lower than time_delete.

    :param int time_delete:
        Timestamp in seconds used for filter rds instances
    :returns:
        List of rds instances IDs
    :rtype:
        [str]
    """
    # define connection
    rds = boto3.client("rds")

    # Define the connection
    paginator = rds.get_paginator("describe_db_instances")
    page_iterator = paginator.paginate()

    # Initialize rds instance list
    rds_instance_list = []

    # Retrieve all rds instance identifier
    for page in page_iterator:
        for instance in page["DBInstances"]:
            if instance["InstanceCreateTime"].timestamp() < time_delete:

                rds_instance = instance["DBInstanceIdentifier"]
                rds_instance_list.insert(0, rds_instance)

    return rds_instance_list


def rds_list_clusters(time_delete):
    """Aurora cluster list function.

    List IDs of all aurora clusters with a timestamp
    lower than time_delete.

    :param int time_delete:
        Timestamp in seconds used for filter aurora clusters
    :returns:
        List of aurora clusters IDs
    :rtype:
        [str]
    """
    # define connection
    rds = boto3.client("rds")

    # Define the connection
    paginator = rds.get_paginator("describe_db_clusters")
    page_iterator = paginator.paginate()

    # Initialize rds cluster list
    rds_cluster_list = []

    # Retrieve all rds cluster identifier
    for page in page_iterator:
        for cluster in page["DBClusters"]:
            if cluster["ClusterCreateTime"].timestamp() < time_delete:

                rds_cluster = cluster["DBClusterIdentifier"]
                rds_cluster_list.insert(0, rds_cluster)

    return rds_cluster_list
