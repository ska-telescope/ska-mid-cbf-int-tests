import argparse
import datetime
import json

import requests

# WARNING: PERMANENTLY DELETES ARTIFACT FILES FROM SYSTEM-TESTS, SO WILL
# PERMANENTLY EFFECT THINGS. DON'T USE UNLESS YOU'RE SURE WHAT YOU'RE DOING.
# Prints and/or deletes all job artifacts associated with jobs before given
# cutoff-time in system-tests repo.

gitlab_datetime_format = "%Y-%m-%dT%H:%M:%S"  # gitlab format removing last 5 chars
project_id = "31568126"  # system-tests project id

def operate_on_artifacts_started_before_cutoff(
    cutoff_datetime_str: str,
    gitlab_pat_token: str,
    estimated_start_page: int,
    estimated_end_page: int,
    to_print: bool,
    to_delete: bool,
) -> None:

    cutoff_datetime = datetime.datetime.strptime(cutoff_datetime_str, gitlab_datetime_format)

    print(f"Cutoff datetime is UTC: {cutoff_datetime}")

    if to_print:
        print("Printing entries before cutoff...")

    if to_delete:
        print("Deleting entries before cutoff...")

    for page_num in range(estimated_start_page, estimated_end_page+1):

        result = requests.get(
            f"https://gitlab.com/api/v4/projects/{project_id}/jobs?per_page=100&page={page_num}",
            headers={"PRIVATE-TOKEN":gitlab_pat_token},
        )
        jobs_data = json.loads(result.text)

        if not isinstance(jobs_data, list):
            raise AssertionError(f"Incorrect return from jobs: {jobs_data}")

        for job_json in jobs_data:
            if job_json["started_at"] is not None:
                start_datetime = datetime.datetime.strptime(
                    job_json["started_at"][:-5], gitlab_datetime_format
                )
                if start_datetime < cutoff_datetime:
                    job_id = job_json["id"]
                    if to_print:
                        print(
                            f"{job_json['started_at'][:-5]} (job id: {job_id}) job artifacts found before cutoff: {job_json['artifacts']}"
                        )
                    if to_delete:
                        result = requests.delete(
                            f"https://gitlab.com/api/v4/projects/{project_id}/jobs/{job_id}/artifacts",
                            headers={"PRIVATE-TOKEN":gitlab_pat_token},
                        )
                        if result.status_code == 204:
                            print(
                                f"{job_json['started_at'][:-5]} (job id: {job_id}) non trace job artifacts deleted"
                            )

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="gitlab_delete_artifacts_before_cutoff",
        description=(
            "WARNING: PERMANENTLY DELETES ARTIFACT FILES FROM SYSTEM-TESTS, SO WILL PERMANENTLY EFFECT THINGS. DON'T USE UNLESS YOU'RE SURE WHAT YOU'RE DOING. "
            "Prints and/or deletes all job artifacts associated with jobs before given cutoff-time in system-tests repo."),
    )
    parser.add_argument("cutoff_datetime", help=f"UTC cutoff time to print/delete things before, in format YYYY-mm-ddTHH:MM:SS")
    parser.add_argument("gitlab_api_pat", help="Gitlab Personal Access Token with api access, maintainer access required")
    parser.add_argument("estimated_start_page", help="Gitlab jobs page to begin search on as explained in Jobs API (100 entries shows on each page)")
    parser.add_argument("estimated_stop_page", help="Gitlab jobs page to end search on as explained in Jobs API (100 entries shows on each page)")
    parser.add_argument("-p", "--print", help="Whether to print artifacts before cutoff or not (one of --print or --delete must be set)", action="store_true")
    parser.add_argument("-d", "--delete", help="Whether to print artifacts before cutoff or not (one of --print or --delete must be set)", action="store_true")
    
    args = parser.parse_args()

    if (not args.print and not args.delete):
        raise AssertionError("One of --print or --delete must be set")
    
    operate_on_artifacts_started_before_cutoff(
        args.cutoff_datetime,
        args.gitlab_api_pat,
        int(args.estimated_start_page),
        int(args.estimated_stop_page),
        args.print,
        args.delete,
    )