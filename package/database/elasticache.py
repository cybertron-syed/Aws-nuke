# -*- coding: utf-8 -*-

"""Module deleting all elasticache resources."""

import logging
import time

import boto3

from botocore.exceptions import ClientError, EndpointConnectionError


def nuke_all_elasticache(older_than_seconds):
    """Elasticache resources deleting function.

    Deleting all elasticache resources with
    a timestamp greater than older_than_seconds.
    That include:
      - clusters
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
    elasticache = boto3.client("elasticache")

    # Test if elasticache resources is present in current aws region
    try:
        elasticache.describe_cache_clusters()
    except EndpointConnectionError:
        print("elasticache resource is not available in this aws region")
        return

    # Nuke all elasticachec clusters
    elasticache_nuke_clusters(time_delete)
    elasticache_nuke_snapshots(time_delete)
    elasticache_nuke_subnets()
    elasticache_nuke_param_groups()


def elasticache_nuke_clusters(time_delete):
    """Elasticache cluster deleting function."""
    # define connection
    elasticache = boto3.client("elasticache")

    # List all elasticache clusters
    elasticache_cluster_list = elasticache_list_clusters(time_delete)

    # Nuke all elasticache clusters
    for cluster in elasticache_cluster_list:

        try:
            elasticache.delete_cache_cluster(CacheClusterId=cluster)
            print("Nuke elasticache cluster {0}".format(cluster))
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "InvalidCacheClusterState":
                logging.info(
                    "cache cluster %s is not in available state", cluster
                )
            else:
                logging.error("Unexpected error: %s", e)


def elasticache_nuke_snapshots(time_delete):
    """Elasticache snapshot deleting function."""
    # define connection
    elasticache = boto3.client("elasticache")

    # List all elasticache snapshots
    elasticache_snapshot_list = elasticache_list_snapshots(time_delete)

    # Nuke all elasticache clusters
    for snapshot in elasticache_snapshot_list:

        try:
            elasticache.delete_snapshot(SnapshotName=snapshot)
            print("Nuke elasticache snapshot {0}".format(snapshot))
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "InvalidSnapshotState":
                logging.info(
                    "cache snapshot %s is not in available state", snapshot
                )
            else:
                logging.error("Unexpected error: %s", e)


def elasticache_nuke_subnets():
    """Elasticache subnet deleting function."""
    # define connection
    elasticache = boto3.client("elasticache")

    # List all elasticache subnets
    elasticache_subnet_list = elasticache_list_subnets()

    # Nuke all elasticache subnets
    for subnet in elasticache_subnet_list:

        try:
            elasticache.delete_cache_subnet_group(CacheSubnetGroupName=subnet)
            print("Nuke elasticache subnet{0}".format(subnet))
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "InvalidCacheSubnetState":
                logging.info("cache %s is not in available state", subnet)
            elif error_code == "InvalidParameterValue":
                logging.info("cache %s cannot be deleted", subnet)
            else:
                logging.error("Unexpected error: %s", e)


def elasticache_nuke_param_groups():
    """Elasticache param group deleting function."""
    # define connection
    elasticache = boto3.client("elasticache")

    # List all elasticache cluster parameters
    elasticache_param_group_list = elasticache_list_param_groups()

    # Nuke all elasticache parameters
    for param in elasticache_param_group_list:

        try:
            elasticache.delete_cache_parameter_group(
                CacheParameterGroupName=param
            )
            print("Nuke elasticache param {0}".format(param))
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "InvalidCacheParameterGroupState":
                logging.info(
                    "cache param %s is not in available state", param
                )
            elif error_code == "InvalidParameterValue":
                logging.info("cache %s param group cannot be deleted", param)
            else:
                logging.error("Unexpected error: %s", e)


def elasticache_list_clusters(time_delete):
    """Elasticache cluster list function.

    List IDs of all elasticache clusters with a timestamp
    lower than time_delete.

    :param int time_delete:
        Timestamp in seconds used for filter elasticache clusters
    :returns:
        List of elasticache clusters IDs
    :rtype:
        [str]
    """
    # define connection
    elasticache = boto3.client("elasticache")

    # Define the connection
    paginator = elasticache.get_paginator("describe_cache_clusters")
    page_iterator = paginator.paginate()

    # Initialize elasticache file system list
    elasticache_cluster_list = []

    # Retrieve all elasticache file system Id
    for page in page_iterator:
        for cluster in page["CacheClusters"]:
            if cluster["CacheClusterCreateTime"].timestamp() < time_delete:

                elasticache_cluster = cluster["CacheClusterId"]
                elasticache_cluster_list.insert(0, elasticache_cluster)

    return elasticache_cluster_list


def elasticache_list_snapshots(time_delete):
    """Elasticache snapshots list function.

    List names of all elasticache snapshots with a timestamp
    lower than time_delete.

    :param int time_delete:
        Timestamp in seconds used for filter elasticache snapshots
    :returns:
        List of elasticache snpashots names
    :rtype:
        [str]
    """
    # define connection
    elasticache = boto3.client("elasticache")

    # Define the connection
    paginator = elasticache.get_paginator("describe_snapshots")
    page_iterator = paginator.paginate()

    # Initialize elasticache snapshot list
    elasticache_snapshot_list = []

    # Retrieve all elasticache snapshot names
    for page in page_iterator:
        for snapshot in page["Snapshots"]:
            if (
                    snapshot["NodeSnapshots"][0][
                        "SnapshotCreateTime"].timestamp() < time_delete
            ):

                elasticache_snapshot = snapshot["SnapshotName"]
                elasticache_snapshot_list.insert(0, elasticache_snapshot)

    return elasticache_snapshot_list


def elasticache_list_subnets():
    """Elasticache subnet list function."""
    # define connection
    elasticache = boto3.client("elasticache")

    # Define the connection
    paginator = elasticache.get_paginator("describe_cache_subnet_groups")
    page_iterator = paginator.paginate()

    # Initialize elasticache subnet list
    elasticache_subnet_list = []

    # Retrieve all elasticache subnet names
    for page in page_iterator:
        for subnet in page["CacheSubnetGroups"]:

            elasticache_subnet = subnet["CacheSubnetGroupName"]
            elasticache_subnet_list.insert(0, elasticache_subnet)

    return elasticache_subnet_list


def elasticache_list_param_groups():
    """Elasticache parameters group list function."""
    # define connection
    elasticache = boto3.client("elasticache")

    # Define the connection
    paginator = elasticache.get_paginator("describe_cache_parameter_groups")
    page_iterator = paginator.paginate()

    # Initialize elasticache param group list
    elasticache_param_group_list = []

    # Retrieve all elasticache param group names
    for page in page_iterator:
        for param_group in page["CacheParameterGroups"]:

            elasticache_param_group = param_group["CacheParameterGroupName"]
            elasticache_param_group_list.insert(0, elasticache_param_group)

    return elasticache_param_group_list
