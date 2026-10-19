export interface paths {
    "/api/v1/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Health */
        get: operations["health_api_v1_health_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/meta/capabilities": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Meta */
        get: operations["meta_api_v1_meta_capabilities_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/map/terrain": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Map Terrain */
        get: operations["map_terrain_api_v1_map_terrain_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/map/terrain/{asset_id}/{sha256}.png": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Bound Terrain Image */
        get: operations["bound_terrain_image_api_v1_map_terrain__asset_id___sha256__png_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/map/surface": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Map Surface */
        get: operations["map_surface_api_v1_map_surface_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/map/terrain.png": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Map Terrain Image */
        get: operations["map_terrain_image_api_v1_map_terrain_png_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/versions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Scenario Versions */
        get: operations["scenario_versions_api_v1_scenarios__scenario_id__versions_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/versions/{version}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Scenario Version */
        get: operations["scenario_version_api_v1_scenarios__scenario_id__versions__version__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Scenarios */
        get: operations["list_scenarios_api_v1_scenarios_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/terrain-assets": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Terrain Assets */
        get: operations["list_terrain_assets_api_v1_terrain_assets_get"];
        put?: never;
        /** Upload Terrain */
        post: operations["upload_terrain_api_v1_terrain_assets_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/terrain-assets/{asset_id}/source": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Download Terrain */
        get: operations["download_terrain_api_v1_terrain_assets__asset_id__source_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/terrain-assets/{asset_id}/package": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Download Terrain Package */
        get: operations["download_terrain_package_api_v1_terrain_assets__asset_id__package_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/terrain-assets/import-package": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Upload Terrain Package */
        post: operations["upload_terrain_package_api_v1_terrain_assets_import_package_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/terrain": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Assign Terrain */
        post: operations["assign_terrain_api_v1_scenarios__scenario_id__terrain_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/examples": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Load Example */
        post: operations["load_example_api_v1_scenarios_examples_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/import": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Import Scenario */
        post: operations["import_scenario_api_v1_scenarios_import_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/communication-template": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Communication Template */
        get: operations["communication_template_api_v1_scenarios__scenario_id__communication_template_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/plans/{plan_id}/playback": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Plan Playback */
        get: operations["plan_playback_api_v1_plans__plan_id__playback_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/plans/{plan_id}/analysis": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Plan Analysis */
        get: operations["plan_analysis_api_v1_plans__plan_id__analysis_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/plans/{plan_id}/flight-profile": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Plan Flight Profile */
        get: operations["plan_flight_profile_api_v1_plans__plan_id__flight_profile_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/plans/{plan_id}/partition": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Plan Partition */
        get: operations["plan_partition_api_v1_plans__plan_id__partition_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/plans/{plan_id}/radio-coverage": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Plan Radio Coverage */
        get: operations["plan_radio_coverage_api_v1_plans__plan_id__radio_coverage_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/plans/{plan_id}/report": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Plan Report */
        get: operations["plan_report_api_v1_plans__plan_id__report_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/what-if": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** What If History */
        get: operations["what_if_history_api_v1_scenarios__scenario_id__what_if_get"];
        put?: never;
        /** What If */
        post: operations["what_if_api_v1_scenarios__scenario_id__what_if_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/origin": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Scenario Origin */
        get: operations["scenario_origin_api_v1_scenarios__scenario_id__origin_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/import-file": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Import File */
        post: operations["import_file_api_v1_scenarios_import_file_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/template": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Template */
        get: operations["template_api_v1_scenarios__scenario_id__template_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Scenario */
        get: operations["get_scenario_api_v1_scenarios__scenario_id__get"];
        /** Update Scenario */
        put: operations["update_scenario_api_v1_scenarios__scenario_id__put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/copy": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Copy Scenario */
        post: operations["copy_scenario_api_v1_scenarios__scenario_id__copy_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/validate": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Validate Input */
        post: operations["validate_input_api_v1_scenarios__scenario_id__validate_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/snapshots": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Make Snapshot */
        post: operations["make_snapshot_api_v1_scenarios__scenario_id__snapshots_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/snapshots/{snapshot_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Snapshot */
        get: operations["get_snapshot_api_v1_snapshots__snapshot_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/snapshots/{snapshot_id}/single-site-analysis": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Single Site Analysis */
        get: operations["single_site_analysis_api_v1_snapshots__snapshot_id__single_site_analysis_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/solve-jobs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Create Job */
        post: operations["create_job_api_v1_solve_jobs_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/solve-jobs/{job_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Job */
        get: operations["get_job_api_v1_solve_jobs__job_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/solve-jobs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Scenario Jobs */
        get: operations["scenario_jobs_api_v1_scenarios__scenario_id__solve_jobs_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/solve-jobs/{job_id}/progress": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Progress */
        get: operations["get_progress_api_v1_solve_jobs__job_id__progress_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/solve-jobs/{job_id}/diagnostics": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Job Diagnostics */
        get: operations["get_job_diagnostics_api_v1_solve_jobs__job_id__diagnostics_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/solve-jobs/{job_id}/cancel": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Cancel Job */
        post: operations["cancel_job_api_v1_solve_jobs__job_id__cancel_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/plans": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Plans */
        get: operations["list_plans_api_v1_scenarios__scenario_id__plans_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/plans/{plan_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Plan */
        get: operations["get_plan_api_v1_plans__plan_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/plans/{plan_id}/comparison": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Compare */
        get: operations["compare_api_v1_plans__plan_id__comparison_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/plans/{plan_id}/confirm": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Confirm */
        post: operations["confirm_api_v1_plans__plan_id__confirm_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/events": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Apply Event */
        post: operations["apply_event_api_v1_events_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/events": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Events */
        get: operations["list_events_api_v1_scenarios__scenario_id__events_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/plans/{plan_id}/export": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Export Plan */
        get: operations["export_plan_api_v1_plans__plan_id__export_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/export": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Export Scenario */
        get: operations["export_scenario_api_v1_scenarios__scenario_id__export_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenarios/{scenario_id}/bundle": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Export Bundle */
        get: operations["export_bundle_api_v1_scenarios__scenario_id__bundle_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/missions/{mission_id}/input-preview": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Input Preview */
        post: operations["input_preview_api_v1_missions__mission_id__input_preview_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/missions/{mission_id}/input-template": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Input Template */
        get: operations["input_template_api_v1_missions__mission_id__input_template_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/missions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Missions */
        get: operations["list_missions_api_v1_missions_get"];
        put?: never;
        /** Create Mission */
        post: operations["create_mission_api_v1_missions_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/missions/{mission_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Mission */
        get: operations["get_mission_api_v1_missions__mission_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Update Mission */
        patch: operations["update_mission_api_v1_missions__mission_id__patch"];
        trace?: never;
    };
    "/api/v1/missions/{mission_id}/draft": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Update Draft */
        put: operations["update_draft_api_v1_missions__mission_id__draft_put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/missions/{mission_id}/clone": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Clone Mission */
        post: operations["clone_mission_api_v1_missions__mission_id__clone_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/missions/{mission_id}/preflight": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Preflight */
        post: operations["preflight_api_v1_missions__mission_id__preflight_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/preflight-reports/{report_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Report */
        get: operations["get_report_api_v1_preflight_reports__report_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/missions/{mission_id}/preflight-reports": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Reports */
        get: operations["list_reports_api_v1_missions__mission_id__preflight_reports_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/plans/{plan_id}/stages": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Stages */
        get: operations["stages_api_v1_plans__plan_id__stages_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/case-library": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Cases */
        get: operations["cases_api_v1_case_library_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/case-library/{case_id}/preview": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Preview */
        get: operations["preview_api_v1_case_library__case_id__preview_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/heuristic-packages": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Heuristic Packages */
        get: operations["heuristic_packages_api_v1_heuristic_packages_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/heuristic-packages/{policy_id}/export": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Export Policy */
        get: operations["export_policy_api_v1_heuristic_packages__policy_id__export_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/heuristic-packages/import": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Import Policy */
        post: operations["import_policy_api_v1_heuristic_packages_import_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/asset-overview": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Overview */
        get: operations["overview_api_v1_asset_overview_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/integrations": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Overview */
        get: operations["overview_api_v1_integrations_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/integrations/configuration": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Configuration */
        get: operations["configuration_api_v1_integrations_configuration_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/meta/operations-capabilities": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Operation Capabilities */
        get: operations["operation_capabilities_api_v1_meta_operations_capabilities_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions/{execution_id}/devices/{device_id}/mission-state": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Device Mission State */
        get: operations["device_mission_state_api_v1_executions__execution_id__devices__device_id__mission_state_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Create Execution */
        post: operations["create_execution_api_v1_executions_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/missions/{mission_id}/executions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Executions */
        get: operations["list_executions_api_v1_missions__mission_id__executions_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions/{execution_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Execution */
        get: operations["get_execution_api_v1_executions__execution_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions/{execution_id}/simulation/actions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Action */
        post: operations["action_api_v1_executions__execution_id__simulation_actions_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions/{execution_id}/events": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Events */
        get: operations["list_events_api_v1_executions__execution_id__events_get"];
        put?: never;
        /** Event */
        post: operations["event_api_v1_executions__execution_id__events_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions/{execution_id}/events/{event_id}/resolve": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Resolve Event */
        post: operations["resolve_event_api_v1_executions__execution_id__events__event_id__resolve_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions/{execution_id}/replan-jobs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Repair */
        post: operations["repair_api_v1_executions__execution_id__replan_jobs_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions/{execution_id}/plan-changes": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Changes */
        get: operations["list_changes_api_v1_executions__execution_id__plan_changes_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions/{execution_id}/plan-changes/{change_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Change */
        get: operations["get_change_api_v1_executions__execution_id__plan_changes__change_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions/{execution_id}/plan-changes/{change_id}/apply": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Apply Change */
        post: operations["apply_change_api_v1_executions__execution_id__plan_changes__change_id__apply_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/devices/{device_id}/capabilities": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Device Capabilities */
        get: operations["device_capabilities_api_v1_devices__device_id__capabilities_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/commands": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Command */
        post: operations["command_api_v1_commands_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/commands/{command_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Command */
        get: operations["get_command_api_v1_commands__command_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions/{execution_id}/analysis": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Analysis */
        get: operations["analysis_api_v1_executions__execution_id__analysis_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions/{execution_id}/stream": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Stream */
        get: operations["stream_api_v1_executions__execution_id__stream_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/executions/{execution_id}/export": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Export Execution */
        get: operations["export_execution_api_v1_executions__execution_id__export_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/execution-archives/import": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Import Archive */
        post: operations["import_archive_api_v1_execution_archives_import_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/execution-archives": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Archives */
        get: operations["list_archives_api_v1_execution_archives_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/execution-archives/{archive_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Archive */
        get: operations["get_archive_api_v1_execution_archives__archive_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/experiments": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Experiments */
        get: operations["list_experiments_api_v1_experiments_get"];
        put?: never;
        /** Create Experiment */
        post: operations["create_experiment_api_v1_experiments_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/experiments/{experiment_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Experiment */
        get: operations["get_experiment_api_v1_experiments__experiment_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/experiments/{experiment_id}/cancel": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Cancel Experiment */
        post: operations["cancel_experiment_api_v1_experiments__experiment_id__cancel_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/experiments/{experiment_id}/export": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Export Experiment */
        get: operations["export_experiment_api_v1_experiments__experiment_id__export_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /**
         * Actor
         * @enum {string}
         */
        Actor: "simulation" | "operator";
        /** AddedSortieId */
        AddedSortieId: string;
        /** ApplyRepair */
        ApplyRepair: {
            /** Expected Revision */
            expected_revision: number;
            /** Idempotency Key */
            idempotency_key: string;
            /** Ack Timeout Device Ids */
            ack_timeout_device_ids?: string[];
        };
        /** AssetOverview */
        AssetOverview: {
            /** Mission Count */
            mission_count: number;
            /** Active Mission Count */
            active_mission_count: number;
            /** Archived Mission Count */
            archived_mission_count: number;
            /** Scenario Count */
            scenario_count: number;
            /** Snapshot Count */
            snapshot_count: number;
            /** Plan Count */
            plan_count: number;
            /** Execution Count */
            execution_count: number;
            /** Event Count */
            event_count: number;
            /** Completed Job Count */
            completed_job_count: number;
            /** Average Solve S */
            average_solve_s: number | null;
            /**
             * Scope
             * @default local_workspace
             * @constant
             */
            scope: "local_workspace";
        };
        /** Base */
        Base: {
            /** Id */
            id: string;
            /** Name */
            name: string;
            coordinates: components["schemas"]["Coordinates"];
            /** Ground Elevation M */
            ground_elevation_m: number | null;
            /** Available */
            available: boolean;
        };
        /** Battery */
        Battery: {
            /** Battery Id */
            battery_id: string;
            /** Compatible Type Id */
            compatible_type_id: string;
            /** Capacity Kwh */
            capacity_kwh: number;
            /** Soc */
            soc: number;
            /** Soh */
            soh: number;
            status: components["schemas"]["Status7"];
            /** Location Id */
            location_id: string;
            /** Available After S */
            available_after_s: number;
        };
        /** BatteryUnavailableEvent */
        BatteryUnavailableEvent: {
            /**
             * Schema Version
             * @constant
             */
            schema_version: "0.1.0-draft";
            /** Event Id */
            event_id: string;
            /** Scenario Id */
            scenario_id: string;
            /** Expected State Version */
            expected_state_version: number;
            /**
             * Event Type
             * @constant
             */
            event_type: "battery.unavailable";
            /**
             * Occurred At
             * Format: date-time
             */
            occurred_at: string;
            /**
             * Received At
             * Format: date-time
             */
            received_at: string;
            /** Effective Time S */
            effective_time_s: number;
            actor: components["schemas"]["Actor"];
            /** Reason */
            reason: string;
            payload: components["schemas"]["Payload1"];
        };
        /** Body_import_archive_api_v1_execution_archives_import_post */
        Body_import_archive_api_v1_execution_archives_import_post: {
            /** File */
            file: string;
        };
        /** Body_import_file_api_v1_scenarios_import_file_post */
        Body_import_file_api_v1_scenarios_import_file_post: {
            /** File */
            file: string;
        };
        /** Body_import_policy_api_v1_heuristic_packages_import_post */
        Body_import_policy_api_v1_heuristic_packages_import_post: {
            /** File */
            file: string;
        };
        /** Body_input_preview_api_v1_missions__mission_id__input_preview_post */
        Body_input_preview_api_v1_missions__mission_id__input_preview_post: {
            /** File */
            file: string;
        };
        /** Body_upload_terrain_api_v1_terrain_assets_post */
        Body_upload_terrain_api_v1_terrain_assets_post: {
            /** File */
            file: string;
            /** Vertical Datum */
            vertical_datum: string;
        };
        /** Body_upload_terrain_package_api_v1_terrain_assets_import_package_post */
        Body_upload_terrain_package_api_v1_terrain_assets_import_package_post: {
            /** File */
            file: string;
        };
        /** BoundWitness */
        BoundWitness: {
            /** Demand Id */
            demand_id: string;
            /** Required Quantity */
            required_quantity: number;
            /** Mass Min Kg */
            mass_min_kg: number;
            /** Volume Min L */
            volume_min_l: number;
            /** Mass Cargo Ids */
            mass_cargo_ids: string[];
            /** Volume Cargo Ids */
            volume_cargo_ids: string[];
        };
        /** Capabilities */
        Capabilities: {
            /**
             * Api Version
             * @constant
             */
            api_version: "v1";
            /** Schema Versions */
            schema_versions: components["schemas"]["SchemaVersion"][];
            /** Solver Ready */
            solver_ready: boolean;
            /** Supported Objectives */
            supported_objectives: components["schemas"]["SupportedObjective"][];
            /** Supported Events */
            supported_events: components["schemas"]["SupportedEvent"][];
            /** Supported Model Scope */
            supported_model_scope: components["schemas"]["SupportedModelScopeEnum"][];
            /** Supported Energy Models */
            supported_energy_models: components["schemas"]["SupportedEnergyModel"][];
            /** Supported Charge Models */
            supported_charge_models: components["schemas"]["SupportedChargeModel"][];
            features: components["schemas"]["Features"];
        };
        /** CapacityBound */
        CapacityBound: {
            /**
             * Model Id
             * @constant
             */
            model_id: "transport_capacity_relaxation_v1";
            /**
             * Status
             * @enum {string}
             */
            status: "ready" | "limited";
            /** Reason */
            reason: string | null;
            /** Snapshot Id */
            snapshot_id: string;
            /** Scenario State Version */
            scenario_state_version: number;
            /** Snapshot Content Hash */
            snapshot_content_hash: string;
            /** Required Box Count */
            required_box_count: number;
            /** Eligible Type Ids */
            eligible_type_ids: string[];
            /** Max Payload Kg */
            max_payload_kg: number | null;
            /** Max Volume L */
            max_volume_l: number | null;
            /** Mass Min Kg */
            mass_min_kg: number | null;
            /** Volume Min L */
            volume_min_l: number | null;
            /** Mass Bound */
            mass_bound: number | null;
            /** Volume Bound */
            volume_bound: number | null;
            /** Sortie Lower Bound */
            sortie_lower_bound: number | null;
            /** Exact */
            exact: {
                [key: string]: string;
            };
            /** Witnesses */
            witnesses: components["schemas"]["BoundWitness"][];
            /** Numeric Policy */
            numeric_policy: string;
            /** Notes */
            notes: string[];
        };
        /** CargoId */
        CargoId: string;
        /** CargoItem */
        CargoItem: {
            /** Cargo Id */
            cargo_id: string;
            /** Demand Id */
            demand_id: string;
            /** Type */
            type: string;
            /** Mass Kg */
            mass_kg: number;
            /** Volume L */
            volume_l: number;
            status: components["schemas"]["Status5"];
            /** Location Id */
            location_id: string;
        };
        /** CargoRepairDifference */
        CargoRepairDifference: {
            /** Cargo Id */
            cargo_id: string;
            /** Previous Plan Id */
            previous_plan_id: string | null;
            /** Previous Sortie Id */
            previous_sortie_id: string | null;
            /** Previous Drone Id */
            previous_drone_id: string | null;
            /** Previous Battery Id */
            previous_battery_id: string | null;
            /** Candidate Sortie Id */
            candidate_sortie_id: string;
            /** Candidate Drone Id */
            candidate_drone_id: string;
            /** Candidate Battery Id */
            candidate_battery_id: string;
            /**
             * Change Kind
             * @enum {string}
             */
            change_kind: "new" | "unchanged" | "modified";
            /** Drone Changed */
            drone_changed: boolean | null;
            /** Battery Changed */
            battery_changed: boolean | null;
            /** Takeoff Delta S */
            takeoff_delta_s: number | null;
            /** Delivery Delta S */
            delivery_delta_s: number | null;
        };
        /** CaseCatalog */
        CaseCatalog: {
            /** Cases */
            cases: components["schemas"]["ExerciseCase"][];
            /** Sources */
            sources: components["schemas"]["SourceReference"][];
        };
        /** ChangeSummary */
        ChangeSummary: {
            /** Preserved Sortie Ids */
            preserved_sortie_ids: components["schemas"]["PreservedSortieId"][];
            /** Removed Sortie Ids */
            removed_sortie_ids: components["schemas"]["RemovedSortieId"][];
            /** Added Sortie Ids */
            added_sortie_ids: components["schemas"]["AddedSortieId"][];
        };
        /** ChargeModel */
        ChargeModel: {
            /** Model Id */
            model_id: string;
            /** Parameters */
            parameters: {
                [key: string]: number;
            };
        };
        /** ChargeWindow */
        ChargeWindow: {
            /** Battery Id */
            battery_id: string;
            /** Type Id */
            type_id: string;
            /** Start S */
            start_s: number;
            /** End S */
            end_s: number;
            /** Is Initial */
            is_initial: boolean;
            /** Sortie Id */
            sortie_id: string | null;
        };
        /** Check */
        Check: {
            code: components["schemas"]["Code"];
            status: components["schemas"]["Status1"];
            /** Object Id */
            object_id: string | null;
            /** Message */
            message: string;
        };
        /** CheckItem */
        CheckItem: {
            /** Code */
            code: string;
            /**
             * Group
             * @enum {string}
             */
            group: "map" | "inventory" | "fleet" | "weather" | "communication" | "model" | "execution";
            /**
             * Status
             * @enum {string}
             */
            status: "passed" | "warning" | "blocked" | "unknown" | "not_applicable";
            /** Message */
            message: string;
            /** Affected Objects */
            affected_objects?: string[];
            /** Field Path */
            field_path?: string | null;
            /** Actual */
            actual?: number | null;
            /** Required */
            required?: number | null;
            /** Unit */
            unit?: string | null;
            /**
             * Action
             * @enum {string}
             */
            action: "region" | "demand" | "fleet" | "checks" | "plans" | "settings";
            /** Source Ref */
            source_ref: string;
        };
        /**
         * Code
         * @enum {string}
         */
        Code: "cargo_unique" | "capacity" | "inventory" | "aircraft" | "battery" | "time_window" | "energy" | "terrain" | "communication" | "restricted_zone" | "ground_resource" | "weather_window";
        /**
         * Code1
         * @enum {string}
         */
        Code1: "SCHEMA_INVALID" | "REFERENCE_INVALID" | "RESOURCE_CONFLICT" | "STATE_VERSION_CONFLICT" | "SNAPSHOT_STALE" | "UNSUPPORTED_SCOPE" | "INPUT_NOT_READY" | "NO_VALIDATED_PLAN" | "UNSUPPORTED_EVENT_STATE" | "SOLVER_BUSY" | "CANCELED" | "EXTERNAL_ASSET_UNAVAILABLE" | "INTERNAL_ERROR";
        /** CommandRequest */
        CommandRequest: {
            /** Execution Id */
            execution_id: string;
            /** Device Id */
            device_id: string;
            /**
             * Command Type
             * @enum {string}
             */
            command_type: "mission.upload" | "mission.activate" | "state.query";
            /** Desired Plan Id */
            desired_plan_id: string;
            /** Expected Execution Revision */
            expected_execution_revision: number;
            /** Idempotency Key */
            idempotency_key: string;
            /**
             * Expires At
             * Format: date-time
             */
            expires_at: string;
            /**
             * Simulation Fault
             * @default none
             * @enum {string}
             */
            simulation_fault: "none" | "reject" | "ack_timeout" | "completion_timeout";
        };
        /** CommandView */
        CommandView: {
            /** Command Id */
            command_id: string;
            /** Execution Id */
            execution_id: string;
            /** Device Id */
            device_id: string;
            /** Command Type */
            command_type: string;
            /**
             * Mode
             * @default simulation
             * @constant
             */
            mode: "simulation";
            /**
             * Status
             * @enum {string}
             */
            status: "queued" | "sent" | "acknowledged" | "succeeded" | "rejected" | "expired" | "indeterminate";
            /** Desired Plan Id */
            desired_plan_id: string;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /**
             * Expires At
             * Format: date-time
             */
            expires_at: string;
            /** Acknowledged At */
            acknowledged_at: string | null;
            /** Completed At */
            completed_at: string | null;
            /** Evidence */
            evidence: string | null;
            observed_state?: components["schemas"]["DeviceMissionState"] | null;
        };
        /** Communication */
        Communication: {
            /**
             * Model Id
             * @constant
             */
            model_id: "projected_dem_radio_v1";
            /** Frequency Mhz */
            frequency_mhz: number;
            /** System Loss Db */
            system_loss_db: number;
            /** Obstruction Loss Db */
            obstruction_loss_db: number;
            /** Sensitivity Dbm */
            sensitivity_dbm: number;
            /** Fading Margin Db */
            fading_margin_db: number;
            gateway: components["schemas"]["RadioGateway"];
            transport: components["schemas"]["RadioEndpoint"];
            relay_access: components["schemas"]["RadioEndpoint"];
            relay_backhaul: components["schemas"]["RadioEndpoint"];
            relay_model: components["schemas"]["RelayModel"];
            /** Relay Drones */
            relay_drones: components["schemas"]["RelayAircraft"][];
            /** Relay Energy */
            relay_energy: components["schemas"]["RelayEnergy"][];
            /** Candidate Stations */
            candidate_stations: components["schemas"]["RelayStation"][];
        };
        /** CommunicationReport */
        CommunicationReport: {
            /**
             * Model Id
             * @constant
             */
            model_id: "projected_dem_radio_v1";
            /** Transport Active S */
            transport_active_s: number;
            /** Direct S */
            direct_s: number;
            /** Relay S */
            relay_s: number;
            /** Coverage Gap S */
            coverage_gap_s: number;
            /** Windows */
            windows: components["schemas"]["CommunicationWindow"][];
        };
        /**
         * CommunicationStatus
         * @enum {string}
         */
        CommunicationStatus: "passed" | "failed" | "not_evaluated";
        /** CommunicationWindow */
        CommunicationWindow: {
            /** Sortie Id */
            sortie_id: string;
            /** Start S */
            start_s: number;
            /** End S */
            end_s: number;
            source: components["schemas"]["Source"];
            /** Relay Sortie Id */
            relay_sortie_id: string | null;
        };
        /** Comparison */
        Comparison: {
            /** Plan Id */
            plan_id: string;
            /** Other Plan Id */
            other_plan_id: string;
            /** Same Snapshot */
            same_snapshot: boolean;
            /** Comparable */
            comparable: boolean;
            /** Warnings */
            warnings: string[];
            /** Differences */
            differences: {
                [key: string]: unknown;
            };
            /** Preserved Sortie Ids */
            preserved_sortie_ids: string[];
            /** Removed Sortie Ids */
            removed_sortie_ids: string[];
            /** Added Sortie Ids */
            added_sortie_ids: string[];
        };
        /** ConfirmRequest */
        ConfirmRequest: {
            /** Expected State Version */
            expected_state_version: number;
            /** Idempotency Key */
            idempotency_key: string;
        };
        /** Confirmation */
        Confirmation: {
            /** Plan Id */
            plan_id: string;
            /** Scenario Id */
            scenario_id: string;
            /** State Version */
            state_version: number;
            /**
             * Confirmation State
             * @constant
             */
            confirmation_state: "confirmed";
            /** Confirmed At */
            confirmed_at: string;
        };
        /** Coordinate */
        Coordinate: number;
        /** Coordinate1 */
        Coordinate1: number;
        /** Coordinate2 */
        Coordinate2: number;
        /** Coordinate3 */
        Coordinate3: number;
        /** Coordinate4 */
        Coordinate4: [
            components["schemas"]["Coordinate4Item"],
            components["schemas"]["Coordinate4Item1"]
        ];
        /** Coordinate4Item */
        Coordinate4Item: number;
        /** Coordinate4Item1 */
        Coordinate4Item1: number;
        /** Coordinate5 */
        Coordinate5: components["schemas"]["Coordinates"][];
        /** Coordinates */
        Coordinates: [
            components["schemas"]["Coordinate"],
            components["schemas"]["Coordinate1"]
        ];
        /** CopyRequest */
        CopyRequest: {
            /** Name */
            name?: string | null;
        };
        /** CoveragePoint */
        CoveragePoint: {
            /** Coordinates */
            coordinates: [
                number,
                number
            ];
            /** Elevation M */
            elevation_m: number | null;
            /**
             * Source
             * @enum {string}
             */
            source: "gateway" | "relay" | "uncovered" | "unknown";
        };
        /**
         * DataOrigin
         * @enum {string}
         */
        DataOrigin: "mock" | "solver" | "imported_historical";
        /**
         * DataOrigin1
         * @enum {string}
         */
        DataOrigin1: "mock" | "user_input" | "verified_dataset";
        /** DeliveryAnalysis */
        DeliveryAnalysis: {
            /** Demands */
            demands: components["schemas"]["DemandDelivery"][];
            /** Weighted Box Delay S */
            weighted_box_delay_s: number;
            /** Late Demand Count */
            late_demand_count: number;
            /** Expected Demand Count */
            expected_demand_count: number;
            /** Hard Violation Count */
            hard_violation_count: number;
        };
        /** DeliveryDeviation */
        DeliveryDeviation: {
            /** Cargo Id */
            cargo_id: string;
            /** Plan Id */
            plan_id: string;
            /** Sortie Id */
            sortie_id: string;
            /** Initial Expected S */
            initial_expected_s: number | null;
            /** Delivered S */
            delivered_s: number;
            /** Difference S */
            difference_s: number | null;
        };
        /** Demand */
        Demand: {
            /** Demand Id */
            demand_id: string;
            /** Site Id */
            site_id: string;
            /** Cargo Type */
            cargo_type: string;
            /** Required Quantity */
            required_quantity: number;
            /** Priority */
            priority: number;
            /** Expected Deadline S */
            expected_deadline_s: number | null;
            /** Hard Deadline S */
            hard_deadline_s: number | null;
            /** Mandatory */
            mandatory: boolean;
        };
        /** DemandAddedEvent */
        DemandAddedEvent: {
            /**
             * Schema Version
             * @constant
             */
            schema_version: "0.1.0-draft";
            /** Event Id */
            event_id: string;
            /** Scenario Id */
            scenario_id: string;
            /** Expected State Version */
            expected_state_version: number;
            /**
             * Event Type
             * @constant
             */
            event_type: "demand.added";
            /**
             * Occurred At
             * Format: date-time
             */
            occurred_at: string;
            /**
             * Received At
             * Format: date-time
             */
            received_at: string;
            /** Effective Time S */
            effective_time_s: number;
            actor: components["schemas"]["Actor"];
            /** Reason */
            reason: string;
            payload: components["schemas"]["Payload2"];
        };
        /** DemandDelivery */
        DemandDelivery: {
            /** Demand Id */
            demand_id: string;
            /** Site Id */
            site_id: string;
            /** Required Quantity */
            required_quantity: number;
            /** Served Quantity */
            served_quantity: number;
            /** Complete S */
            complete_s: number | null;
            /** Expected Deadline S */
            expected_deadline_s: number | null;
            /** Hard Deadline S */
            hard_deadline_s: number | null;
            /** Delay S */
            delay_s: number | null;
            /** Hard Satisfied */
            hard_satisfied: boolean | null;
        };
        /** DeviceApplication */
        DeviceApplication: {
            /** Device Id */
            device_id: string;
            /** Desired Plan Id */
            desired_plan_id: string | null;
            /** Active Plan Id */
            active_plan_id: string;
            /**
             * Upload State
             * @enum {string}
             */
            upload_state: "queued" | "acknowledged" | "succeeded" | "indeterminate" | "expired" | "rejected";
            /**
             * Activation State
             * @enum {string}
             */
            activation_state: "not_started" | "active" | "indeterminate";
            /** Command Id */
            command_id: string;
            /** Activation Command Id */
            activation_command_id?: string | null;
        };
        /** DeviceCapabilities */
        DeviceCapabilities: {
            /** Device Id */
            device_id: string;
            /**
             * Adapter
             * @default simulation
             * @constant
             */
            adapter: "simulation";
            /**
             * Mode
             * @default simulation
             * @constant
             */
            mode: "simulation";
            /**
             * Supports Upload
             * @default true
             * @constant
             */
            supports_upload: true;
            /**
             * Supports Inflight Replacement
             * @default false
             * @constant
             */
            supports_inflight_replacement: false;
            /**
             * Supports Future Schedule Update
             * @default true
             * @constant
             */
            supports_future_schedule_update: true;
            /** Command Types */
            command_types: ("mission.upload" | "mission.activate" | "state.query")[];
            /**
             * Real Device Connected
             * @default false
             * @constant
             */
            real_device_connected: false;
        };
        /** DeviceMissionState */
        DeviceMissionState: {
            /** Execution Id */
            execution_id: string;
            /** Device Id */
            device_id: string;
            /**
             * Mode
             * @default simulation
             * @constant
             */
            mode: "simulation";
            /** Revision */
            revision: number;
            /** Active Plan Id */
            active_plan_id: string;
            /** Uploaded Plan Id */
            uploaded_plan_id: string | null;
            /** Uploaded Content Sha256 */
            uploaded_content_sha256?: string | null;
            /** Last Upload Command Id */
            last_upload_command_id?: string | null;
            /** Last Activation Command Id */
            last_activation_command_id?: string | null;
            /**
             * Updated At
             * Format: date-time
             */
            updated_at: string;
            /**
             * Observed At
             * Format: date-time
             */
            observed_at: string;
            /**
             * Real Device Connected
             * @default false
             * @constant
             */
            real_device_connected: false;
        };
        /** Diagnostic */
        Diagnostic: {
            /** Code */
            code: string;
            /** Message */
            message: string;
            /** Field Path */
            field_path: string | null;
            /** Object Id */
            object_id: string | null;
        };
        /** DraftImportPreview */
        DraftImportPreview: {
            draft: components["schemas"]["MissionDraft"];
            /** Row Count */
            row_count: number;
            /** Notices */
            notices: string[];
        };
        /** Drone */
        Drone: {
            /** Drone Id */
            drone_id: string;
            /** Type Id */
            type_id: string;
            status: components["schemas"]["Status6"];
            /** Location Id */
            location_id: string;
            /** Available After S */
            available_after_s: number;
        };
        /** DroneType */
        DroneType: {
            /** Type Id */
            type_id: string;
            /** Max Payload Kg */
            max_payload_kg: number;
            /** Max Volume L */
            max_volume_l: number;
            /** Cruise Speed Mps */
            cruise_speed_mps: number;
            /** Climb Speed Mps */
            climb_speed_mps: number;
            /** Descent Speed Mps */
            descent_speed_mps: number;
            /** Prepare Duration S */
            prepare_duration_s: number;
            /** Turnaround Duration S */
            turnaround_duration_s: number;
            /** Handover Fixed S */
            handover_fixed_s: number;
            /** Handover Per Box S */
            handover_per_box_s: number;
            /** Empty Mass Kg */
            empty_mass_kg: number;
            energy_model: components["schemas"]["EnergyModel"];
            charge_model: components["schemas"]["ChargeModel"];
        };
        /** DroneUnavailableEvent */
        DroneUnavailableEvent: {
            /**
             * Schema Version
             * @constant
             */
            schema_version: "0.1.0-draft";
            /** Event Id */
            event_id: string;
            /** Scenario Id */
            scenario_id: string;
            /** Expected State Version */
            expected_state_version: number;
            /**
             * Event Type
             * @constant
             */
            event_type: "drone.unavailable";
            /**
             * Occurred At
             * Format: date-time
             */
            occurred_at: string;
            /**
             * Received At
             * Format: date-time
             */
            received_at: string;
            /** Effective Time S */
            effective_time_s: number;
            actor: components["schemas"]["Actor"];
            /** Reason */
            reason: string;
            payload: components["schemas"]["Payload"];
        };
        /** EnergyModel */
        EnergyModel: {
            /** Model Id */
            model_id: string;
            /** Parameters */
            parameters: {
                [key: string]: number;
            };
        };
        /** Engine */
        Engine: {
            engine_type: components["schemas"]["EngineType"];
            /** Policy Id */
            policy_id: string | null;
            /** Version */
            version: string | null;
            origin: components["schemas"]["Origin1"];
            /** Sha256 */
            sha256: string | null;
            /** Ranking Evaluations */
            ranking_evaluations: number;
            /** Fallback Evaluations */
            fallback_evaluations: number;
        };
        /**
         * EngineType
         * @enum {string}
         */
        EngineType: "standard" | "eoh";
        /** Error1 */
        Error1: {
            code: components["schemas"]["Code1"];
            /** Message */
            message: string;
            /** Field Path */
            field_path: string | null;
            /** Details */
            details: {
                [key: string]: unknown;
            };
            /** Request Id */
            request_id: string;
        };
        /**
         * Event
         * @description Implementation draft: additive zero-time relay component withdrawal RFC-013; preserving previous event JSON; pending A/B review.
         */
        Event: components["schemas"]["DroneUnavailableEvent"] | components["schemas"]["BatteryUnavailableEvent"] | components["schemas"]["DemandAddedEvent"] | components["schemas"]["RelayEnergyUnavailableEvent"];
        /** EventReceipt */
        EventReceipt: {
            event: components["schemas"]["Event"];
            /** State Version After */
            state_version_after: number;
            /** Applied */
            applied: boolean;
        };
        /** EventResolution */
        EventResolution: {
            /** Expected Revision */
            expected_revision: number;
            /** Idempotency Key */
            idempotency_key: string;
            /**
             * Action
             * @constant
             */
            action: "withdraw_misreport";
            /** Reason */
            reason: string;
        };
        /** ExampleRequest */
        ExampleRequest: {
            /**
             * Example
             * @default compact
             * @enum {string}
             */
            example: "compact" | "contest";
        };
        /** ExecutionAnalysis */
        ExecutionAnalysis: {
            /** Execution Id */
            execution_id: string;
            /** Facts Cursor */
            facts_cursor: number;
            /**
             * Source
             * @default simulation
             * @constant
             */
            source: "simulation";
            /** Allocated Quantity */
            allocated_quantity: number;
            /** Delivered Quantity */
            delivered_quantity: number;
            /** Unserved Quantity */
            unserved_quantity: number;
            /** Delivery Rows */
            delivery_rows: components["schemas"]["ExecutionFact"][];
            /** Initial Plan Id */
            initial_plan_id: string;
            /** Active Plan Ids */
            active_plan_ids: string[];
            /** Event Count */
            event_count: number;
            /** Change Count */
            change_count: number;
            /** Deviation Rows */
            deviation_rows?: components["schemas"]["DeliveryDeviation"][];
        };
        /** ExecutionArchiveSummary */
        ExecutionArchiveSummary: {
            /** Archive Id */
            archive_id: string;
            /** Execution Id */
            execution_id: string;
            /** Mission Name */
            mission_name: string;
            /**
             * Imported At
             * Format: date-time
             */
            imported_at: string;
            /**
             * Captured At
             * Format: date-time
             */
            captured_at: string;
            /** Captured Time S */
            captured_time_s: number;
            /** Captured Status */
            captured_status: string;
            /** Fact Count */
            fact_count: number;
            /** Plan Count */
            plan_count: number;
            /** Content Sha256 */
            content_sha256: string;
            /**
             * Read Only
             * @default true
             * @constant
             */
            read_only: true;
        };
        /** ExecutionArchiveView */
        ExecutionArchiveView: {
            summary: components["schemas"]["ExecutionArchiveSummary"];
            bundle: components["schemas"]["ExecutionBundle"];
            /** Plans */
            plans: components["schemas"]["Plan"][];
            /** Snapshots */
            snapshots: components["schemas"]["Snapshot"][];
            analysis: components["schemas"]["ExecutionAnalysis"];
        };
        /** ExecutionBundle */
        ExecutionBundle: {
            /**
             * Bundle Version
             * @constant
             */
            bundle_version: "execution-simulation-v2";
            /**
             * Source
             * @constant
             */
            source: "simulation";
            /**
             * Is Flight Controller File
             * @constant
             */
            is_flight_controller_file: false;
            /**
             * Captured At
             * Format: date-time
             */
            captured_at: string;
            /** Mission Name */
            mission_name: string;
            execution: components["schemas"]["ExecutionView"];
            /** Events */
            events: components["schemas"]["ExecutionEventView"][];
            /** Changes */
            changes: components["schemas"]["RepairView"][];
            /** Commands */
            commands: components["schemas"]["CommandView"][];
            /** Documents */
            documents: components["schemas"]["FrozenDocument"][];
            /** Content Sha256 */
            content_sha256: string;
        };
        /** ExecutionCreate */
        ExecutionCreate: {
            /** Mission Id */
            mission_id: string;
            /** Confirmed Plan Id */
            confirmed_plan_id: string;
            /** Expected Revision */
            expected_revision: number;
            /**
             * Mode
             * @default simulation
             * @constant
             */
            mode: "simulation";
            /**
             * Seed
             * @default 42
             */
            seed: number;
            /** Idempotency Key */
            idempotency_key: string;
        };
        /** ExecutionEventInput */
        ExecutionEventInput: {
            /** Event Id */
            event_id: string;
            /** Expected Revision */
            expected_revision: number;
            /**
             * Event Type
             * @enum {string}
             */
            event_type: "drone.unavailable" | "battery.unavailable" | "demand.added" | "site.unavailable" | "weather.changed";
            /** Object Id */
            object_id?: string | null;
            demand?: components["schemas"]["Demand"] | null;
            /** Cargo Items */
            cargo_items?: components["schemas"]["CargoItem"][];
            weather?: components["schemas"]["Weather"] | null;
            /** Reason */
            reason: string;
        };
        /** ExecutionEventView */
        ExecutionEventView: {
            /** Event Id */
            event_id: string;
            /** Execution Id */
            execution_id: string;
            /** Event Type */
            event_type: string;
            /** Object Id */
            object_id: string | null;
            /** Reason */
            reason: string;
            /** Time S */
            time_s: number;
            /** Facts Cursor */
            facts_cursor: number;
            /** Affected Sortie Ids */
            affected_sortie_ids: string[];
            /** Propagated Sortie Ids */
            propagated_sortie_ids: string[];
            /** Preserved Sortie Ids */
            preserved_sortie_ids: string[];
            /** Committed Sortie Ids */
            committed_sortie_ids: string[];
            /** Missing Inventory */
            missing_inventory: number;
            /**
             * Status
             * @enum {string}
             */
            status: "recorded" | "requires_manual" | "withdrawn";
            weather?: components["schemas"]["Weather"] | null;
            /** Resolved At */
            resolved_at?: string | null;
            /** Resolution Reason */
            resolution_reason?: string | null;
            impact?: components["schemas"]["ExecutionImpact"] | null;
        };
        /** ExecutionFact */
        ExecutionFact: {
            /** Fact Id */
            fact_id: string;
            /** Cursor */
            cursor: number;
            /** Time S */
            time_s: number;
            /**
             * Kind
             * @enum {string}
             */
            kind: "loaded" | "takeoff" | "delivered" | "returned" | "released" | "battery_ready" | "plan_adopted" | "relay_started" | "relay_arrived" | "relay_service_started" | "relay_service_ended" | "relay_returned" | "relay_released" | "relay_energy_ready";
            /** Plan Id */
            plan_id: string;
            /** Sortie Id */
            sortie_id: string | null;
            /** Drone Id */
            drone_id: string | null;
            /** Battery Id */
            battery_id: string | null;
            /** Component Id */
            component_id?: string | null;
            /** Cargo Ids */
            cargo_ids: string[];
            /**
             * Source
             * @default simulation
             * @constant
             */
            source: "simulation";
        };
        /** ExecutionImpact */
        ExecutionImpact: {
            /**
             * Scope
             * @constant
             */
            scope: "frozen_transport_resource_precedence";
            /** Time S */
            time_s: number;
            /** Facts Cursor */
            facts_cursor: number;
            /**
             * Ground Model
             * @enum {string}
             */
            ground_model: "unlimited" | "conservative_common_release";
            /** Nodes */
            nodes: components["schemas"]["ImpactNode"][];
            /** Edges */
            edges: components["schemas"]["ImpactEdge"][];
        };
        /** ExecutionSchedulePart */
        ExecutionSchedulePart: {
            /** Plan Id */
            plan_id: string;
            /** Sortie Ids */
            sortie_ids: string[];
            /** Relay Sortie Ids */
            relay_sortie_ids?: string[];
            /**
             * Role
             * @enum {string}
             */
            role: "initial" | "commitment" | "future";
        };
        /** ExecutionView */
        ExecutionView: {
            /** Execution Id */
            execution_id: string;
            /** Mission Id */
            mission_id: string;
            /**
             * Mode
             * @constant
             */
            mode: "simulation";
            /** Initial Plan Id */
            initial_plan_id: string;
            /** Desired Plan Id */
            desired_plan_id: string;
            /**
             * Status
             * @enum {string}
             */
            status: "ready" | "running" | "paused" | "completed";
            /** Revision */
            revision: number;
            /** Facts Cursor */
            facts_cursor: number;
            /** Time S */
            time_s: number;
            /** Speed */
            speed: number;
            /** Seed */
            seed: number;
            /** Connected */
            connected: boolean;
            /** Schedule Parts */
            schedule_parts: components["schemas"]["ExecutionSchedulePart"][];
            /** Delivered Cargo Ids */
            delivered_cargo_ids: string[];
            /** Applied Event Ids */
            applied_event_ids?: string[];
            /** Facts */
            facts: components["schemas"]["ExecutionFact"][];
            /** Telemetry */
            telemetry: components["schemas"]["TelemetrySample"][];
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /**
             * Updated At
             * Format: date-time
             */
            updated_at: string;
        };
        /** ExerciseCase */
        ExerciseCase: {
            /** Case Id */
            case_id: string;
            /** Version */
            version: string;
            /** Name */
            name: string;
            /** Subtitle */
            subtitle: string;
            /**
             * Category
             * @enum {string}
             */
            category: "mountain" | "flood" | "communication" | "urgent";
            /**
             * Template
             * @enum {string}
             */
            template: "compact" | "contest" | "compact_joint" | "contest_joint";
            /** Description */
            description: string;
            /** Learning Goals */
            learning_goals: string[];
            /** Source Ids */
            source_ids: string[];
            /** Site Count */
            site_count: number;
            /** Cargo Count */
            cargo_count: number;
            /** Communication */
            communication: boolean;
            /** Data Statement */
            data_statement: string;
        };
        /** ExperimentArtifact */
        ExperimentArtifact: {
            /** Case Id */
            case_id: string;
            /**
             * Name
             * @enum {string}
             */
            name: "input.json" | "outcome.json" | "progress.json" | "worker.log";
            /** Byte Count */
            byte_count: number;
            /** Content Sha256 */
            content_sha256: string;
            /** Content Base64 */
            content_base64: string;
        };
        /** ExperimentBundle */
        ExperimentBundle: {
            /**
             * Bundle Version
             * @default experiment-v1
             * @constant
             */
            bundle_version: "experiment-v1";
            /**
             * Captured At
             * Format: date-time
             */
            captured_at: string;
            run: components["schemas"]["ExperimentView"];
            /** Documents */
            documents: components["schemas"]["FrozenDocument"][];
            /** Artifacts */
            artifacts: components["schemas"]["ExperimentArtifact"][];
            /** Missing Artifacts */
            missing_artifacts: string[];
            /** Content Sha256 */
            content_sha256: string;
        };
        /** ExperimentCase */
        ExperimentCase: {
            /** Case Id */
            case_id: string;
            /**
             * Method
             * @enum {string}
             */
            method: "quick" | "improve" | "dependency" | "full_recompute";
            /** Repair Reference Id */
            repair_reference_id?: string | null;
            /** Calculation Method */
            calculation_method?: ("dependency_local" | "full_recompute") | null;
            repair_difference?: components["schemas"]["RepairDifference"] | null;
            /**
             * Objective
             * @enum {string}
             */
            objective: "time" | "energy" | "balanced";
            /** Seed */
            seed: number;
            /** Time Limit S */
            time_limit_s: number;
            /**
             * Status
             * @enum {string}
             */
            status: "queued" | "dispatching" | "running" | "completed" | "failed" | "canceled";
            job: components["schemas"]["SolveJob"] | null;
            /** First Feasible S */
            first_feasible_s: number | null;
            /** Candidate Count */
            candidate_count: number | null;
            /** Runtime S */
            runtime_s: number | null;
            /** Energy Kwh */
            energy_kwh: number | null;
            /** Makespan S */
            makespan_s: number | null;
            /** Last Delivery S */
            last_delivery_s: number | null;
            /** Weighted Tardiness S */
            weighted_tardiness_s: number | null;
            /** Min Return Soc */
            min_return_soc: number | null;
            /** Allocated Quantity */
            allocated_quantity: number | null;
            /** Model Scope */
            model_scope: string[];
            /** Validation Status */
            validation_status: string | null;
            /** Diagnostics */
            diagnostics: components["schemas"]["Diagnostic"][];
            /** Message */
            message: string | null;
        };
        /** ExperimentEnvironment */
        ExperimentEnvironment: {
            /** Service Source Sha256 */
            service_source_sha256: string;
            /** Git Commit */
            git_commit: string | null;
            /** Git Worktree Dirty */
            git_worktree_dirty: boolean;
            /** Python Version */
            python_version: string;
            /** Platform */
            platform: string;
            /** Processor */
            processor: string | null;
            /** Logical Cpu Count */
            logical_cpu_count: number | null;
            /** Ortools Version */
            ortools_version: string;
            /** Numpy Version */
            numpy_version: string;
            /**
             * Worker Serial Limit
             * @default 1
             * @constant
             */
            worker_serial_limit: 1;
            /**
             * Cp Sat Threads
             * @default 1
             * @constant
             */
            cp_sat_threads: 1;
            /** Cache Policy */
            cache_policy: string;
        };
        /** ExperimentGroup */
        ExperimentGroup: {
            /** Method */
            method: string;
            /** Objective */
            objective: string;
            /** Total */
            total: number;
            /** Finished */
            finished: number;
            /** Feasible */
            feasible: number;
            /** Failed Or Unvalidated */
            failed_or_unvalidated: number;
            /** Canceled */
            canceled: number;
            /** Runtime Sample Count */
            runtime_sample_count: number;
            /** Runtime P50 S */
            runtime_p50_s: number | null;
            /** Runtime P95 S */
            runtime_p95_s: number | null;
            /** Feasible Energy Median Kwh */
            feasible_energy_median_kwh: number | null;
            /** Feasible Makespan Median S */
            feasible_makespan_median_s: number | null;
        };
        /** ExperimentRequest */
        ExperimentRequest: {
            /** Name */
            name: string;
            /** Source Snapshot Id */
            source_snapshot_id: string;
            /**
             * Suite
             * @enum {string}
             */
            suite: "strategy" | "search" | "repair";
            /** Repair Reference Id */
            repair_reference_id?: string | null;
            /**
             * Objective
             * @default time
             * @enum {string}
             */
            objective: "time" | "energy" | "balanced";
            /**
             * Objective Policy
             * @default tradeoff_v2
             * @enum {string}
             */
            objective_policy: "deadline_first_v1" | "tradeoff_v2";
            /** Seeds */
            seeds: number[];
            /** Time Limit S */
            time_limit_s: number;
            /** Idempotency Key */
            idempotency_key: string;
            /** Engine Type */
            engine_type?: ("standard" | "eoh") | null;
            /** Heuristic Policy Id */
            heuristic_policy_id?: string | null;
            /** Heuristic Policy Sha256 */
            heuristic_policy_sha256?: string | null;
        };
        /** ExperimentView */
        ExperimentView: {
            /** Experiment Id */
            experiment_id: string;
            /** Name */
            name: string;
            /** Source Snapshot Id */
            source_snapshot_id: string;
            /** Source Content Hash */
            source_content_hash: string;
            /** Snapshot Id */
            snapshot_id: string;
            /** Snapshot Content Hash */
            snapshot_content_hash: string;
            /** Data Origin */
            data_origin: string;
            /**
             * Suite
             * @enum {string}
             */
            suite: "strategy" | "search" | "repair";
            repair_context?: components["schemas"]["RepairExperimentContext"] | null;
            /**
             * Objective Policy
             * @enum {string}
             */
            objective_policy: "deadline_first_v1" | "tradeoff_v2";
            /**
             * Status
             * @enum {string}
             */
            status: "queued" | "running" | "completed" | "canceled";
            /** Cancel Requested */
            cancel_requested: boolean;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Finished At */
            finished_at: string | null;
            environment: components["schemas"]["ExperimentEnvironment"];
            /** Cases */
            cases: components["schemas"]["ExperimentCase"][];
            /** Groups */
            groups: components["schemas"]["ExperimentGroup"][];
            /** Message */
            message: string;
            /** Engine Type */
            engine_type?: ("standard" | "eoh") | null;
            /** Heuristic Policy Id */
            heuristic_policy_id?: string | null;
            /** Heuristic Policy Sha256 */
            heuristic_policy_sha256?: string | null;
        };
        /** Features */
        Features: {
            /** Partial Service */
            partial_service: boolean;
            /** Relay Coordination */
            relay_coordination: boolean;
            /** Execution State */
            execution_state: boolean;
            /** Dem Validation */
            dem_validation: boolean;
            /** What If */
            what_if: boolean;
        };
        /** FlightProfile */
        FlightProfile: {
            /** Plan Id */
            plan_id: string;
            /** Snapshot Id */
            snapshot_id: string;
            /** Scenario State Version */
            scenario_state_version: number;
            /** Sortie Id */
            sortie_id: string;
            /** Drone Id */
            drone_id: string;
            /** Drone Type Id */
            drone_type_id: string;
            /** Terrain Asset Id */
            terrain_asset_id: string | null;
            /** Terrain Sha256 */
            terrain_sha256: string | null;
            /** Vertical Datum */
            vertical_datum: string | null;
            /** Total Distance M */
            total_distance_m: number;
            /** Total Climb M */
            total_climb_m: number;
            /** Total Descent M */
            total_descent_m: number;
            /** Flight Time S */
            flight_time_s: number;
            /** Modeled Energy Kwh */
            modeled_energy_kwh: number;
            /** Horizontal Energy Kwh */
            horizontal_energy_kwh: number;
            /** Climb Energy Kwh */
            climb_energy_kwh: number;
            /** Plan Sortie Energy Kwh */
            plan_sortie_energy_kwh: number | null;
            /** Legs */
            legs: components["schemas"]["FlightProfileLeg"][];
            /** Notice */
            notice: string;
        };
        /** FlightProfileLeg */
        FlightProfileLeg: {
            /** Leg Index */
            leg_index: number;
            /** From Id */
            from_id: string;
            /** To Id */
            to_id: string;
            /** Distance M */
            distance_m: number;
            /** Start Distance M */
            start_distance_m: number;
            /** End Distance M */
            end_distance_m: number;
            /** Start Work Elevation M */
            start_work_elevation_m: number;
            /** End Work Elevation M */
            end_work_elevation_m: number;
            /** Cruise Elevation M */
            cruise_elevation_m: number;
            /** Climb M */
            climb_m: number;
            /** Descent M */
            descent_m: number;
            /** Clearance Required M */
            clearance_required_m: number;
            /** Payload Kg */
            payload_kg: number;
            /** Flight Time S */
            flight_time_s: number;
            /** Energy Kwh */
            energy_kwh: number;
            /** Horizontal Energy Kwh */
            horizontal_energy_kwh: number;
            /** Climb Energy Kwh */
            climb_energy_kwh: number;
            /** Terrain Checked */
            terrain_checked: boolean;
            /** Terrain Maximum M */
            terrain_maximum_m: number | null;
            /** Cruise Clearance Margin M */
            cruise_clearance_margin_m: number | null;
            /** Samples */
            samples: components["schemas"]["FlightProfileSample"][];
        };
        /** FlightProfileSample */
        FlightProfileSample: {
            /** Distance M */
            distance_m: number;
            /** Longitude */
            longitude: number;
            /** Latitude */
            latitude: number;
            /** Ground Elevation M */
            ground_elevation_m: number | null;
            /** Cruise Elevation M */
            cruise_elevation_m: number;
        };
        /** FrozenDocument */
        FrozenDocument: {
            /**
             * Kind
             * @enum {string}
             */
            kind: "plan" | "snapshot" | "event_input" | "event_resolution" | "repair_reference" | "repair_evidence";
            /** Document Id */
            document_id: string;
            /** Payload Json */
            payload_json: string;
            /** Sha256 */
            sha256: string;
        };
        /** Geometry */
        Geometry: {
            /**
             * Type
             * @constant
             */
            type: "Polygon";
            /** Coordinates */
            coordinates: components["schemas"]["Coordinate5"][];
        };
        /** GroundResourceAddition */
        GroundResourceAddition: {
            /**
             * Prep Slots
             * @default 0
             */
            prep_slots: number;
            /**
             * Charging Ports
             * @default 0
             */
            charging_ports: number;
        };
        /** HTTPValidationError */
        HTTPValidationError: {
            /** Detail */
            detail?: components["schemas"]["ValidationError"][];
        };
        /** Health */
        Health: {
            /**
             * Service Id
             * @default yuanhang-rescue
             * @constant
             */
            service_id: "yuanhang-rescue";
            /** Workspace Id */
            workspace_id: string;
            /** Status */
            status: string;
            /** Service Version */
            service_version: string;
            /** Solver Ready */
            solver_ready: boolean;
            /** Service Source Sha256 */
            service_source_sha256: string;
            /** Runtime Id */
            runtime_id: string;
        };
        /** HeuristicPackage */
        HeuristicPackage: {
            /** Policy Id */
            policy_id: string;
            /** Name */
            name: string;
            /** Version */
            version: string;
            /**
             * Origin
             * @enum {string}
             */
            origin: "rule_initialization" | "eoh_offline";
            /** Description */
            description: string;
            /** Sha256 */
            sha256: string;
            /**
             * Online Network Required
             * @constant
             */
            online_network_required: false;
            /** Evolution Record */
            evolution_record: {
                [key: string]: unknown;
            } | null;
        };
        /** ImpactEdge */
        ImpactEdge: {
            /** From Node Id */
            from_node_id: string;
            /** To Node Id */
            to_node_id: string;
            /**
             * Resource Kind
             * @enum {string}
             */
            resource_kind: "drone" | "battery";
            /** Resource Id */
            resource_id: string;
        };
        /** ImpactNode */
        ImpactNode: {
            /** Node Id */
            node_id: string;
            /** Plan Id */
            plan_id: string;
            /** Sortie Id */
            sortie_id: string;
            /** Drone Id */
            drone_id: string;
            /** Battery Id */
            battery_id: string;
            /** Cargo Ids */
            cargo_ids: string[];
            /** Prepare Start S */
            prepare_start_s: number;
            /** Takeoff S */
            takeoff_s: number;
            /** Return S */
            return_s: number;
            /** Drone Released S */
            drone_released_s: number;
            /** Battery Released S */
            battery_released_s: number;
            /** Direct */
            direct: boolean;
            /** Affected */
            affected: boolean;
            /** Committed */
            committed: boolean;
        };
        /** ImportPreview */
        ImportPreview: {
            scenario: components["schemas"]["Scenario"];
            /** Row Count */
            row_count: number;
            /** Issues */
            issues: {
                [key: string]: unknown;
            }[];
        };
        /** InitialCharge */
        InitialCharge: {
            /** Battery Id */
            battery_id: string;
            /** Start S */
            start_s: number;
            /** End S */
            end_s: number;
            /** From Soc */
            from_soc: number;
            /**
             * To Soc
             * @constant
             */
            to_soc: 1;
        };
        /** IntegrationEndpoint */
        IntegrationEndpoint: {
            /** Name */
            name: string;
            /**
             * Method
             * @enum {string}
             */
            method: "GET" | "POST";
            /** Path */
            path: string;
            /** Description */
            description: string;
        };
        /** IntegrationOverview */
        IntegrationOverview: {
            /**
             * Runtime Mode
             * @default simulation
             * @constant
             */
            runtime_mode: "simulation";
            /**
             * Installed Adapter
             * @default SimulationAdapter
             * @constant
             */
            installed_adapter: "SimulationAdapter";
            /**
             * Real Device Connected
             * @default false
             * @constant
             */
            real_device_connected: false;
            /**
             * External Model Calls Enabled
             * @default false
             * @constant
             */
            external_model_calls_enabled: false;
            /**
             * Telemetry Transport
             * @default server_sent_events
             * @constant
             */
            telemetry_transport: "server_sent_events";
            /** Command States */
            command_states: string[];
            /** Endpoints */
            endpoints: components["schemas"]["IntegrationEndpoint"][];
            /** Adapter Methods */
            adapter_methods: string[];
        };
        /** Items */
        Items: {
            /** Cargo Id */
            cargo_id: string;
            /** Demand Id */
            demand_id: string;
            /** Type */
            type: string;
            /** Mass Kg */
            mass_kg: number;
            /** Volume L */
            volume_l: number;
            status: components["schemas"]["Status8"];
            /** Location Id */
            location_id: string;
        };
        /** ItemsModel */
        ItemsModel: {
            /** Demand Id */
            demand_id: string;
            /** Site Id */
            site_id: string;
            /** Cargo Type */
            cargo_type: string;
            /** Required Quantity */
            required_quantity: number;
            /** Priority */
            priority: number;
            /** Expected Deadline S */
            expected_deadline_s: number | null;
            /** Hard Deadline S */
            hard_deadline_s: number | null;
            /** Mandatory */
            mandatory: boolean;
        };
        /**
         * JobState
         * @enum {string}
         */
        JobState: "queued" | "running" | "completed" | "failed" | "canceled";
        /** JointMetrics */
        JointMetrics: {
            /** Relay Energy Kwh */
            relay_energy_kwh: number;
            /** Joint Energy Kwh */
            joint_energy_kwh: number;
            /** Joint Makespan S */
            joint_makespan_s: number;
            /** Relay Sortie Count */
            relay_sortie_count: number;
        };
        /** JointSearch */
        JointSearch: {
            /**
             * Method
             * @constant
             */
            method: "fixed_grouping_joint_cp_v1";
            /** Status */
            status: string;
            /** Station Count */
            station_count: number;
            /** Coverage Atom Count */
            coverage_atom_count: number;
            /** Relay Slot Limit */
            relay_slot_limit: number;
            /** Stages */
            stages: components["schemas"]["Stage"][];
        };
        /** Metrics */
        Metrics: {
            /** Last Delivery S */
            last_delivery_s: number | null;
            /** Makespan S */
            makespan_s: number | null;
            /** Energy Kwh */
            energy_kwh: number | null;
            /** Cost Cny */
            cost_cny: null;
            /** Sortie Count */
            sortie_count: number;
            /** Unserved Demand Count */
            unserved_demand_count: number;
            /** Mandatory Served Count */
            mandatory_served_count: number;
            /** Mandatory Total Count */
            mandatory_total_count: number;
            /** Min Return Soc */
            min_return_soc: number | null;
        };
        /** MissionCreate */
        MissionCreate: {
            /** Name */
            name: string;
            /**
             * Mode
             * @default simulation
             * @enum {string}
             */
            mode: "simulation" | "planning_assist";
            /**
             * Template
             * @default blank
             * @enum {string}
             */
            template: "blank" | "compact" | "contest" | "compact_joint" | "contest_joint";
            /** Scenario Id */
            scenario_id?: string | null;
            /** Case Id */
            case_id?: string | null;
            /** Idempotency Key */
            idempotency_key: string;
        };
        /** MissionDraft */
        MissionDraft: {
            /**
             * Start Time
             * Format: date-time
             */
            start_time: string;
            /** Timezone */
            timezone: string;
            base: components["schemas"]["Base"] | null;
            /** Sites */
            sites: components["schemas"]["Site"][];
            /** Demands */
            demands: components["schemas"]["Demand"][];
            /** Cargo Items */
            cargo_items: components["schemas"]["CargoItem"][];
            /** Drone Types */
            drone_types: components["schemas"]["DroneType"][];
            /** Drones */
            drones: components["schemas"]["Drone"][];
            /** Batteries */
            batteries: components["schemas"]["Battery"][];
            terrain: components["schemas"]["Terrain"];
            policy: components["schemas"]["Policy"];
            /** Restricted Zones */
            restricted_zones?: components["schemas"]["RestrictedZone"][] | null;
            resource_limits?: components["schemas"]["ResourceLimits"] | null;
            communication?: components["schemas"]["Communication"] | null;
            weather?: components["schemas"]["Weather"] | null;
        };
        /** MissionDraftUpdate */
        MissionDraftUpdate: {
            /** Expected Revision */
            expected_revision: number;
            draft: components["schemas"]["MissionDraft"];
            /**
             * Publish
             * @default false
             */
            publish: boolean;
        };
        /** MissionUpdate */
        MissionUpdate: {
            /** Expected Revision */
            expected_revision: number;
            /** Name */
            name?: string | null;
            /** Archived */
            archived?: boolean | null;
        };
        /** MissionView */
        MissionView: {
            /** Mission Id */
            mission_id: string;
            /** Source Case Id */
            source_case_id?: string | null;
            /** Name */
            name: string;
            /**
             * Mode
             * @enum {string}
             */
            mode: "simulation" | "planning_assist";
            /** Timezone */
            timezone: string;
            /**
             * Lifecycle
             * @enum {string}
             */
            lifecycle: "draft" | "planning" | "ready" | "executing" | "paused" | "completed" | "archived";
            /** Revision */
            revision: number;
            /** Current Scenario Id */
            current_scenario_id: string | null;
            /** Active Plan Id */
            active_plan_id: string | null;
            /** Active Execution Id */
            active_execution_id: string | null;
            draft: components["schemas"]["MissionDraft"];
            /**
             * Updated At
             * Format: date-time
             */
            updated_at: string;
            /** Site Count */
            site_count: number;
            /** Cargo Count */
            cargo_count: number;
            /**
             * Next Action
             * @enum {string}
             */
            next_action: "prepare" | "plans" | "execute" | "review";
        };
        /**
         * Mode
         * @enum {string}
         */
        Mode: "simulation" | "planning_assist";
        /**
         * ModelScopeEnum
         * @enum {string}
         */
        ModelScopeEnum: "cargo_unique" | "capacity" | "inventory" | "aircraft" | "battery" | "time_window" | "energy" | "terrain" | "communication" | "restricted_zone" | "ground_resource" | "weather_window";
        /** NominalBatch */
        NominalBatch: {
            /** Batch Id */
            batch_id: string;
            /** Site Id */
            site_id: string;
            /** Type Id */
            type_id: string;
            /** Cargo Ids */
            cargo_ids: string[];
            /** Mass Kg */
            mass_kg: number;
            /** Volume L */
            volume_l: number;
            /** Duration S */
            duration_s: number;
            /** Energy Kwh */
            energy_kwh: number;
            /** Return Soc */
            return_soc: number;
        };
        /** NominalCapacity */
        NominalCapacity: {
            /** Site Id */
            site_id: string;
            /** Type Id */
            type_id: string;
            /** Capacity Kg */
            capacity_kg: number | null;
            /** Max Volume L */
            max_volume_l: number;
            /** Nominal Energy Kwh */
            nominal_energy_kwh: number | null;
            /** Allowed Energy Kwh */
            allowed_energy_kwh: number | null;
            /** Empty Energy Kwh */
            empty_energy_kwh: number | null;
            /** Full Energy Kwh */
            full_energy_kwh: number | null;
            /** Roundtrip Distance M */
            roundtrip_distance_m: number | null;
            /** Terrain Evaluated */
            terrain_evaluated: boolean;
            /**
             * Limit
             * @enum {string}
             */
            limit: "empty_infeasible" | "rated_payload" | "energy" | "unavailable";
            /** Root Width Kg */
            root_width_kg: number | null;
            /** Residual Kwh */
            residual_kwh: number | null;
            /** Reason */
            reason: string | null;
        };
        /** NominalMetrics */
        NominalMetrics: {
            /** Sortie Count */
            sortie_count: number;
            /** Energy Kwh */
            energy_kwh: number;
            /** Operation S */
            operation_s: number;
            /** Min Return Soc */
            min_return_soc: number | null;
        };
        /** NominalParameters */
        NominalParameters: {
            /** Min Return Soc */
            min_return_soc: number;
            /** Nominal Soc */
            nominal_soc: number;
            /** Nominal Soh */
            nominal_soh: number;
            /** Max Count States Per Site */
            max_count_states_per_site: number;
            /** Priority */
            priority: string[];
        };
        /** NominalReport */
        NominalReport: {
            /**
             * Model Id
             * @constant
             */
            model_id: "single_site_nominal_transport_v1";
            /**
             * Status
             * @enum {string}
             */
            status: "limited" | "partial" | "complete";
            /** Reason */
            reason: string | null;
            /** Snapshot Id */
            snapshot_id: string;
            /** Scenario Id */
            scenario_id: string;
            /** Scenario State Version */
            scenario_state_version: number;
            /** Snapshot Content Hash */
            snapshot_content_hash: string;
            /** Required Box Count */
            required_box_count: number;
            /** Available Box Count */
            available_box_count: number;
            parameters: components["schemas"]["NominalParameters"];
            /** Analysis Input Hash */
            analysis_input_hash: string;
            /** Capacities */
            capacities: components["schemas"]["NominalCapacity"][];
            /** Sites */
            sites: components["schemas"]["NominalSite"][];
            /** Batches */
            batches: components["schemas"]["NominalBatch"][];
            metrics: components["schemas"]["NominalMetrics"] | null;
            single_box_baseline: components["schemas"]["NominalMetrics"] | null;
            greedy_baseline: components["schemas"]["NominalMetrics"] | null;
            /** Sensitivity */
            sensitivity: components["schemas"]["NominalSensitivity"][];
            /** Audit Checks */
            audit_checks: string[];
            /** Runtime S */
            runtime_s: number;
            /** Notes */
            notes: string[];
        };
        /** NominalSensitivity */
        NominalSensitivity: {
            /** Min Return Soc */
            min_return_soc: number;
            /**
             * Status
             * @enum {string}
             */
            status: "complete" | "partial";
            metrics: components["schemas"]["NominalMetrics"] | null;
        };
        /** NominalSite */
        NominalSite: {
            /** Site Id */
            site_id: string;
            /**
             * Status
             * @enum {string}
             */
            status: "complete" | "limited" | "infeasible";
            /** Reason */
            reason: string | null;
            /** Count States */
            count_states: number;
            /** Box Count */
            box_count: number;
            metrics: components["schemas"]["NominalMetrics"] | null;
        };
        /**
         * Objective
         * @enum {string}
         */
        Objective: "time" | "energy" | "balanced";
        /**
         * ObjectivePolicy
         * @enum {string}
         */
        ObjectivePolicy: "deadline_first_v1" | "tradeoff_v2";
        /** OperationCapabilities */
        OperationCapabilities: {
            /** Modes */
            modes: "simulation"[];
            /**
             * Real Dispatch
             * @default false
             * @constant
             */
            real_dispatch: false;
            /**
             * Sitl
             * @default false
             * @constant
             */
            sitl: false;
            /**
             * Persistent Simulation
             * @default true
             * @constant
             */
            persistent_simulation: true;
            /**
             * Commitment Repair
             * @default transport_committed_prefix_future_only
             * @constant
             */
            commitment_repair: "transport_committed_prefix_future_only";
            /**
             * Relay Simulation
             * @default true
             * @constant
             */
            relay_simulation: true;
            /**
             * Weather Information
             * @default true
             * @constant
             */
            weather_information: true;
            /**
             * Weather Thresholds
             * @default true
             * @constant
             */
            weather_thresholds: true;
            /**
             * Weather Energy
             * @default false
             * @constant
             */
            weather_energy: false;
            /**
             * Learning Search
             * @default false
             * @constant
             */
            learning_search: false;
            /**
             * Position Source
             * @default business_model_phases
             * @constant
             */
            position_source: "business_model_phases";
        };
        /**
         * Origin1
         * @enum {string}
         */
        Origin1: "standard" | "rule_initialization" | "eoh_offline";
        /** PartitionAssignment */
        PartitionAssignment: {
            /** Task Id */
            task_id: string;
            /** Start S */
            start_s: number;
            /** End S */
            end_s: number;
            /** Original Resource Id */
            original_resource_id: string;
            /** Allocated Resource Id */
            allocated_resource_id: string;
            /** Needs Addition */
            needs_addition: boolean;
        };
        /** PartitionAtom */
        PartitionAtom: {
            /** Atom Id */
            atom_id: string;
            /** Site Ids */
            site_ids: string[];
            /** Transport Sortie Ids */
            transport_sortie_ids: string[];
            /** Relay Sortie Ids */
            relay_sortie_ids: string[];
        };
        /** PartitionCandidate */
        PartitionCandidate: {
            /** Groups */
            groups: components["schemas"]["PartitionGroup"][];
            /** Configuration */
            configuration: components["schemas"]["PartitionConfiguration"][];
            /** Normalized Deficit */
            normalized_deficit: number;
            /** Normalized Size */
            normalized_size: number;
            /** Workload Cv2 */
            workload_cv2: number;
            /** Objective Exact */
            objective_exact: {
                [key: string]: string;
            };
            /** Fits Inventory */
            fits_inventory: boolean;
        };
        /** PartitionConfiguration */
        PartitionConfiguration: {
            /** Resource Key */
            resource_key: string;
            /** Inventory */
            inventory: number;
            /** Pooled Required */
            pooled_required: number;
            /** Partition Required */
            partition_required: number;
            /** Extra Vs Pool */
            extra_vs_pool: number;
            /** Shortfall */
            shortfall: number;
            /** Unallocated Stock */
            unallocated_stock: number;
        };
        /** PartitionEdge */
        PartitionEdge: {
            /**
             * Kind
             * @enum {string}
             */
            kind: "transport" | "relay";
            /** Task Id */
            task_id: string;
            /** Site Ids */
            site_ids: string[];
        };
        /** PartitionGroup */
        PartitionGroup: {
            /** Group Id */
            group_id: string;
            /** Atom Ids */
            atom_ids: string[];
            /** Site Ids */
            site_ids: string[];
            /** Transport Sortie Ids */
            transport_sortie_ids: string[];
            /** Relay Sortie Ids */
            relay_sortie_ids: string[];
            /** Box Count */
            box_count: number;
            /** Workload S */
            workload_s: number;
            /** Resources */
            resources: components["schemas"]["PartitionResourcePeak"][];
        };
        /** PartitionPooledRequirement */
        PartitionPooledRequirement: {
            /** Resource Key */
            resource_key: string;
            /** Required Count */
            required_count: number;
        };
        /** PartitionReport */
        PartitionReport: {
            /**
             * Model Id
             * @constant
             */
            model_id: "frozen_joint_homogeneous_v1";
            /**
             * Status
             * @enum {string}
             */
            status: "ready" | "limited";
            /** Reason */
            reason: string | null;
            /** Plan Id */
            plan_id: string;
            /** Snapshot Id */
            snapshot_id: string;
            /** Scenario State Version */
            scenario_state_version: number;
            /** Snapshot Content Hash */
            snapshot_content_hash: string;
            /** Source Plan Hash */
            source_plan_hash: string;
            /** Max Atoms */
            max_atoms: number;
            /** Atoms */
            atoms: components["schemas"]["PartitionAtom"][];
            /** Edges */
            edges: components["schemas"]["PartitionEdge"][];
            /** Resource Classes */
            resource_classes: components["schemas"]["PartitionResourceClass"][];
            /** Pooled Requirements */
            pooled_requirements: components["schemas"]["PartitionPooledRequirement"][];
            /** Variants */
            variants: components["schemas"]["PartitionVariant"][];
            /** Audit Checks */
            audit_checks: string[];
            /** Notes */
            notes: string[];
        };
        /** PartitionResourceClass */
        PartitionResourceClass: {
            /** Key */
            key: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "drone" | "battery" | "relay_drone" | "relay_energy" | "prep" | "charger";
            /** Type Id */
            type_id: string;
            /** Label */
            label: string;
            /** Inventory */
            inventory: number;
        };
        /** PartitionResourcePeak */
        PartitionResourcePeak: {
            /** Resource Key */
            resource_key: string;
            /** Required Count */
            required_count: number;
            /** Peak At S */
            peak_at_s: number | null;
            /** Peak Task Ids */
            peak_task_ids: string[];
            /** Assignments */
            assignments: components["schemas"]["PartitionAssignment"][];
        };
        /** PartitionVariant */
        PartitionVariant: {
            /**
             * Group Count
             * @enum {integer}
             */
            group_count: 2 | 3;
            /** Candidate Count */
            candidate_count: number;
            /**
             * Status
             * @enum {string}
             */
            status: "available" | "not_possible";
            /** Reason */
            reason: string | null;
            resource_first: components["schemas"]["PartitionCandidate"] | null;
            balanced_first: components["schemas"]["PartitionCandidate"] | null;
        };
        /** Payload */
        Payload: {
            /** Drone Id */
            drone_id: string;
        };
        /** Payload1 */
        Payload1: {
            /** Battery Id */
            battery_id: string;
        };
        /** Payload2 */
        Payload2: {
            demand: components["schemas"]["ItemsModel"];
            /** Cargo Items */
            cargo_items: components["schemas"]["Items"][];
        };
        /** Payload3 */
        Payload3: {
            /** Component Id */
            component_id: string;
        };
        /** Plan */
        Plan: {
            /**
             * Schema Version
             * @constant
             */
            schema_version: "0.1.0-draft";
            /** Plan Id */
            plan_id: string;
            /** Scenario Id */
            scenario_id: string;
            /** Snapshot Id */
            snapshot_id: string;
            /** Scenario State Version */
            scenario_state_version: number;
            data_origin: components["schemas"]["DataOrigin"];
            objective: components["schemas"]["Objective"];
            solver_status: components["schemas"]["SolverStatus"];
            /** Has Validated Plan */
            has_validated_plan: boolean;
            /** Model Scope */
            model_scope: components["schemas"]["ModelScopeEnum"][];
            metrics: components["schemas"]["Metrics"];
            /** Sorties */
            sorties: components["schemas"]["Sortie"][];
            /** Unserved Demand Ids */
            unserved_demand_ids: components["schemas"]["UnservedDemandId"][];
            validation: components["schemas"]["Validation"];
            /**
             * Generated At
             * Format: date-time
             */
            generated_at: string;
            /** Solver Notes */
            solver_notes: components["schemas"]["SolverNote"][];
            /** Parent Plan Id */
            parent_plan_id: string | null;
            /** Event Id */
            event_id: string | null;
            change_summary: components["schemas"]["ChangeSummary"] | null;
            /** Initial Charges */
            initial_charges?: components["schemas"]["InitialCharge"][] | null;
            /** Relay Sorties */
            relay_sorties?: components["schemas"]["RelaySortie"][] | null;
            joint_metrics?: components["schemas"]["JointMetrics"] | null;
            communication_report?: components["schemas"]["CommunicationReport"] | null;
            joint_search?: components["schemas"]["JointSearch"] | null;
            /**
             * @description Absent means legacy soft-deadline-first. tradeoff_v2 ranks the selected time/energy goal first, soft lateness second. Hard constraints and full service remain mandatory.
             * @default deadline_first_v1
             */
            objective_policy: components["schemas"]["ObjectivePolicy"] | null;
            engine?: components["schemas"]["Engine"] | null;
        };
        /** PlanAnalysis */
        PlanAnalysis: {
            /** Plan Id */
            plan_id: string;
            /** Snapshot Id */
            snapshot_id: string;
            /** Scenario State Version */
            scenario_state_version: number;
            /** Model Scope */
            model_scope: string[];
            capacity_bound?: components["schemas"]["CapacityBound"] | null;
            resource_limits: components["schemas"]["ResourceLimits"] | null;
            /** Prep Peak */
            prep_peak: number;
            /** Charge Wait S */
            charge_wait_s: number;
            delivery: components["schemas"]["DeliveryAnalysis"];
            /** Resources */
            resources: components["schemas"]["ResourceUsage"][];
            /** Charge Windows */
            charge_windows: components["schemas"]["ChargeWindow"][];
            /** Charge Peak */
            charge_peak: number;
            /** Charge Peak By Type */
            charge_peak_by_type: {
                [key: string]: number;
            };
            /** Min Hard Slack S */
            min_hard_slack_s: number | null;
            /** Notes */
            notes: string[];
        };
        /** PlanSummary */
        PlanSummary: {
            /** Plan Id */
            plan_id: string;
            /** Snapshot Id */
            snapshot_id: string;
            /** Scenario Id */
            scenario_id: string;
            /** Scenario State Version */
            scenario_state_version: number;
            /** Objective */
            objective: string;
            /**
             * Objective Policy
             * @default deadline_first_v1
             * @enum {string}
             */
            objective_policy: "deadline_first_v1" | "tradeoff_v2";
            /** Generated At */
            generated_at: string;
            /** Solver Status */
            solver_status: string;
            /** Metrics */
            metrics: {
                [key: string]: unknown;
            };
            /** Confirmed At */
            confirmed_at: string | null;
            /**
             * Algorithm Mode
             * @default quick
             * @enum {string}
             */
            algorithm_mode: "quick" | "improve" | "replan";
            /** Source Plan Id */
            source_plan_id?: string | null;
            engine?: components["schemas"]["Engine"] | null;
        };
        /** Playback */
        Playback: {
            /** Plan Id */
            plan_id: string;
            /** Snapshot Id */
            snapshot_id: string;
            /**
             * Position Semantics
             * @constant
             */
            position_semantics: "schematic_linear_interpolation";
            /**
             * Is Execution Fact
             * @constant
             */
            is_execution_fact: false;
            /** Phases */
            phases: components["schemas"]["PlaybackPhase"][];
        };
        /** PlaybackPhase */
        PlaybackPhase: {
            /** Sortie Id */
            sortie_id: string;
            /** Drone Id */
            drone_id: string;
            /**
             * Phase
             * @enum {string}
             */
            phase: "prepare" | "flight" | "handover" | "return";
            /** Start S */
            start_s: number;
            /** End S */
            end_s: number;
            /** From Coordinates */
            from_coordinates: [
                number,
                number
            ];
            /** To Coordinates */
            to_coordinates: [
                number,
                number
            ];
        };
        /** Policy */
        Policy: {
            /** Min Return Soc */
            min_return_soc: number;
            /** Requires Terrain */
            requires_terrain: boolean;
            /** Requires Communication */
            requires_communication: boolean;
            /**
             * Delivery Time Policy
             * @constant
             */
            delivery_time_policy: "station_end";
            /**
             * Cost Model Available
             * @constant
             */
            cost_model_available: false;
        };
        /** PreflightReport */
        PreflightReport: {
            /** Report Id */
            report_id: string;
            /** Mission Id */
            mission_id: string;
            /** Scenario Id */
            scenario_id: string | null;
            /** State Version */
            state_version: number | null;
            /** Snapshot Id */
            snapshot_id: string | null;
            /** Check Kind */
            check_kind: string;
            /** Checks */
            checks: components["schemas"]["CheckItem"][];
            /** Blocking Count */
            blocking_count: number;
            /** Warning Count */
            warning_count: number;
            /** Validity Fingerprint */
            validity_fingerprint: string;
            /**
             * Checked At
             * Format: date-time
             */
            checked_at: string;
        };
        /** PreflightRequest */
        PreflightRequest: {
            /** Expected Revision */
            expected_revision: number;
            /**
             * Check Kind
             * @default planning_readiness
             * @enum {string}
             */
            check_kind: "planning_readiness" | "simulation_readiness" | "real_dispatch";
            /** Plan Id */
            plan_id?: string | null;
        };
        /** PreservedSortieId */
        PreservedSortieId: string;
        /** Progress */
        Progress: {
            /** Stage */
            stage: string;
            /** Elapsed S */
            elapsed_s: number;
            /** Candidate Count */
            candidate_count: number;
        };
        /** RadioCoverage */
        RadioCoverage: {
            /** Plan Id */
            plan_id: string;
            /** Snapshot Id */
            snapshot_id: string;
            /** Terrain Sha256 */
            terrain_sha256: string;
            /** Vertical Datum */
            vertical_datum: string | null;
            /** Relay Sortie Id */
            relay_sortie_id: string | null;
            /** Relay Service Start S */
            relay_service_start_s: number | null;
            /** Relay Service End S */
            relay_service_end_s: number | null;
            /** Relay Backhaul Available */
            relay_backhaul_available: boolean | null;
            /** Altitude Agl M */
            altitude_agl_m: number;
            /** Bounds */
            bounds: [
                number,
                number,
                number,
                number
            ];
            /** Grid Size */
            grid_size: number;
            /** Points */
            points: components["schemas"]["CoveragePoint"][];
            /** Complete */
            complete: boolean;
            /** Notice */
            notice: string;
        };
        /** RadioEndpoint */
        RadioEndpoint: {
            /** Tx Power Dbm */
            tx_power_dbm: number;
            /** Gain Dbi */
            gain_dbi: number;
        };
        /** RadioGateway */
        RadioGateway: {
            /** Tx Power Dbm */
            tx_power_dbm: number;
            /** Gain Dbi */
            gain_dbi: number;
            /** Antenna Height M */
            antenna_height_m: number;
        };
        /** RelayAircraft */
        RelayAircraft: {
            /** Drone Id */
            drone_id: string;
            status: components["schemas"]["Status2"];
            /** Location Id */
            location_id: string;
            /** Available After S */
            available_after_s: number;
        };
        /** RelayEnergy */
        RelayEnergy: {
            /** Component Id */
            component_id: string;
            /** Capacity Kwh */
            capacity_kwh: number;
            /** Soc */
            soc: number;
            /** Soh */
            soh: number;
            status: components["schemas"]["Status3"];
            /** Location Id */
            location_id: string;
            /** Available After S */
            available_after_s: number;
        };
        /** RelayEnergyUnavailableEvent */
        RelayEnergyUnavailableEvent: {
            /**
             * Schema Version
             * @constant
             */
            schema_version: "0.1.0-draft";
            /** Event Id */
            event_id: string;
            /** Scenario Id */
            scenario_id: string;
            /** Expected State Version */
            expected_state_version: number;
            /**
             * Event Type
             * @constant
             */
            event_type: "relay_energy.unavailable";
            /**
             * Occurred At
             * Format: date-time
             */
            occurred_at: string;
            /**
             * Received At
             * Format: date-time
             */
            received_at: string;
            /** Effective Time S */
            effective_time_s: number;
            actor: components["schemas"]["Actor"];
            /** Reason */
            reason: string;
            payload: components["schemas"]["Payload3"];
        };
        /** RelayModel */
        RelayModel: {
            /** Mass Kg */
            mass_kg: number;
            /** Cruise Speed Mps */
            cruise_speed_mps: number;
            /** Climb Speed Mps */
            climb_speed_mps: number;
            /** Descent Speed Mps */
            descent_speed_mps: number;
            /** Cruise Power Kw */
            cruise_power_kw: number;
            /** Hover Power Kw */
            hover_power_kw: number;
            /** Radio Power Kw */
            radio_power_kw: number;
            /** Climb Efficiency */
            climb_efficiency: number;
            /** Prepare Duration S */
            prepare_duration_s: number;
            /** Link Duration S */
            link_duration_s: number;
            /** Turnaround Duration S */
            turnaround_duration_s: number;
            /** Full Charge S */
            full_charge_s: number;
            /** Max Agl M */
            max_agl_m: number;
            /** Min Return Soc */
            min_return_soc: number;
        };
        /** RelaySortie */
        RelaySortie: {
            /** Relay Sortie Id */
            relay_sortie_id: string;
            /** Drone Id */
            drone_id: string;
            /** Component Id */
            component_id: string;
            /** Station Id */
            station_id: string;
            /** Station Coordinates */
            station_coordinates: [
                components["schemas"]["StationCoordinate"],
                components["schemas"]["StationCoordinate1"]
            ];
            /** Station Agl M */
            station_agl_m: number;
            /** Station Elevation M */
            station_elevation_m: number;
            /** Prepare Start S */
            prepare_start_s: number;
            /** Takeoff S */
            takeoff_s: number;
            /** Arrival S */
            arrival_s: number;
            /** Service Start S */
            service_start_s: number;
            /** Service End S */
            service_end_s: number;
            /** Return S */
            return_s: number;
            /** Drone Released S */
            drone_released_s: number;
            /** Charge Start S */
            charge_start_s: number;
            /** Component Released S */
            component_released_s: number;
            /** Energy Kwh */
            energy_kwh: number;
            /** Return Soc */
            return_soc: number;
            route_geometry: components["schemas"]["RouteGeometry"];
        };
        /** RelayStation */
        RelayStation: {
            /** Station Id */
            station_id: string;
            /** Coordinates */
            coordinates: [
                components["schemas"]["Coordinate2"],
                components["schemas"]["Coordinate3"]
            ];
            /** Agl M */
            agl_m: number;
        };
        /** RemovedSortieId */
        RemovedSortieId: string;
        /** RepairDifference */
        RepairDifference: {
            /** Committed Quantity */
            committed_quantity: number;
            /** Retained Future Sortie Count */
            retained_future_sortie_count: number;
            /** Drone Reassigned Quantity */
            drone_reassigned_quantity: number;
            /** Battery Reassigned Quantity */
            battery_reassigned_quantity: number;
            /** Time Shifted Quantity */
            time_shifted_quantity: number;
            /** Unchanged Future Quantity */
            unchanged_future_quantity: number;
            /** New Quantity */
            new_quantity: number;
            /** Rows */
            rows: components["schemas"]["CargoRepairDifference"][];
        };
        /** RepairExperimentContext */
        RepairExperimentContext: {
            /** Source Reference Id */
            source_reference_id: string;
            /** Execution Id */
            execution_id: string;
            /** Execution Revision */
            execution_revision: number;
            /** Facts Cursor */
            facts_cursor: number;
            /** Time S */
            time_s: number;
            /** Event Fingerprint */
            event_fingerprint: string;
            /** Committed Quantity */
            committed_quantity: number;
            /** Comparison Input Sha256 */
            comparison_input_sha256: string;
        };
        /** RepairRequest */
        RepairRequest: {
            /** Expected Revision */
            expected_revision: number;
            /** Idempotency Key */
            idempotency_key: string;
            /**
             * Objective
             * @default time
             * @enum {string}
             */
            objective: "time" | "energy" | "balanced";
            /**
             * Time Limit S
             * @default 10
             */
            time_limit_s: number;
            /**
             * Repair Policy
             * @default dependency
             * @enum {string}
             */
            repair_policy: "dependency" | "full";
        };
        /** RepairView */
        RepairView: {
            /** Change Id */
            change_id: string;
            /** Execution Id */
            execution_id: string;
            /** Execution Revision */
            execution_revision: number;
            /** Facts Cursor */
            facts_cursor: number;
            /** Event Fingerprint */
            event_fingerprint: string;
            /** Committed Parts */
            committed_parts: components["schemas"]["ExecutionSchedulePart"][];
            /** Committed Cargo Ids */
            committed_cargo_ids: string[];
            /** Future Not Before S */
            future_not_before_s: number;
            job: components["schemas"]["SolveJob"] | null;
            /** Candidate Plan Id */
            candidate_plan_id: string | null;
            /**
             * Status
             * @enum {string}
             */
            status: "computing" | "ready" | "no_remaining" | "applying" | "failed" | "partially_applied" | "applied";
            /** Message */
            message: string;
            /** Changed Cargo Ids */
            changed_cargo_ids: string[];
            /** Retained Cargo Ids */
            retained_cargo_ids: string[];
            /** Applications */
            applications?: components["schemas"]["DeviceApplication"][];
            /** Repair Policy */
            repair_policy?: ("dependency" | "full") | null;
            /** Calculation Method */
            calculation_method?: ("dependency_local" | "full_recompute") | null;
            /** Repair Reference Id */
            repair_reference_id?: string | null;
            diff?: components["schemas"]["RepairDifference"] | null;
        };
        /** ResourceAddition */
        ResourceAddition: {
            /** Type Id */
            type_id: string;
            /**
             * Drones
             * @default 0
             */
            drones: number;
            /**
             * Batteries
             * @default 0
             */
            batteries: number;
            /** Battery Capacity Kwh */
            battery_capacity_kwh?: number | null;
        };
        /** ResourceLimits */
        ResourceLimits: {
            /** Prep Slots */
            prep_slots: number;
            /** Charging Ports */
            charging_ports: number;
        };
        /** ResourceUsage */
        ResourceUsage: {
            /**
             * Kind
             * @enum {string}
             */
            kind: "drone" | "battery" | "relay_drone" | "relay_energy";
            /** Resource Id */
            resource_id: string;
            /** Type Id */
            type_id: string;
            /** Sortie Count */
            sortie_count: number;
            /** Occupied S */
            occupied_s: number;
            /** Flight S */
            flight_s: number;
            /** Energy Kwh */
            energy_kwh: number;
            /** Horizon S */
            horizon_s: number;
            /** Utilization */
            utilization: number;
        };
        /** RestrictedZone */
        RestrictedZone: {
            /** Zone Id */
            zone_id: string;
            /** Name */
            name: string;
            /** Buffer M */
            buffer_m: number;
            geometry: components["schemas"]["Geometry"];
        };
        /** RouteGeometry */
        RouteGeometry: {
            /**
             * Type
             * @constant
             */
            type: "LineString";
            /** Coordinates */
            coordinates: components["schemas"]["Coordinate4"][];
        };
        /** RouteGeometry1 */
        RouteGeometry1: {
            /**
             * Type
             * @constant
             */
            type: "LineString";
            /** Coordinates */
            coordinates: components["schemas"]["Coordinates"][];
        };
        /** Scenario */
        Scenario: {
            /**
             * Schema Version
             * @constant
             */
            schema_version: "0.1.0-draft";
            /** Scenario Id */
            scenario_id: string;
            /** Name */
            name: string;
            /** State Version */
            state_version: number;
            mode: components["schemas"]["Mode"];
            data_origin: components["schemas"]["DataOrigin1"];
            /**
             * Start Time
             * Format: date-time
             */
            start_time: string;
            /** Timezone */
            timezone: string;
            /**
             * Coordinate System
             * @constant
             */
            coordinate_system: "EPSG:4326";
            terrain: components["schemas"]["Terrain"];
            base: components["schemas"]["Base"];
            /** Sites */
            sites: components["schemas"]["Site"][];
            /** Demands */
            demands: components["schemas"]["Demand"][];
            /** Cargo Items */
            cargo_items: components["schemas"]["CargoItem"][];
            /** Drone Types */
            drone_types: components["schemas"]["DroneType"][];
            /** Drones */
            drones: components["schemas"]["Drone"][];
            /** Batteries */
            batteries: components["schemas"]["Battery"][];
            policy: components["schemas"]["Policy"];
            /** Restricted Zones */
            restricted_zones?: components["schemas"]["RestrictedZone"][] | null;
            resource_limits?: components["schemas"]["ResourceLimits"] | null;
            communication?: components["schemas"]["Communication"] | null;
            weather?: components["schemas"]["Weather"] | null;
        };
        /** ScenarioOrigin */
        ScenarioOrigin: {
            /**
             * Kind
             * @default what_if
             * @constant
             */
            kind: "what_if";
            /** Source Scenario Id */
            source_scenario_id: string;
            /** Source State Version */
            source_state_version: number;
            /** Source Content Hash */
            source_content_hash: string;
            /** Source Plan Id */
            source_plan_id: string | null;
            /**
             * Transformation Version
             * @default what_if_v1
             * @enum {string}
             */
            transformation_version: "what_if_v1" | "what_if_v2_ground_capacity";
            parameters: components["schemas"]["WhatIfRequest"];
            /** Changes */
            changes: string[];
        };
        /** ScenarioSummary */
        ScenarioSummary: {
            /** Scenario Id */
            scenario_id: string;
            /** Name */
            name: string;
            /** State Version */
            state_version: number;
            /** Data Origin */
            data_origin: string;
            /** Site Count */
            site_count: number;
            /** Cargo Count */
            cargo_count: number;
            /** Drone Count */
            drone_count: number;
            /** Battery Count */
            battery_count: number;
            /** Active Plan Id */
            active_plan_id: string | null;
            /** Updated At */
            updated_at: string;
        };
        /** ScenarioUpdate */
        ScenarioUpdate: {
            /** Expected State Version */
            expected_state_version: number;
            scenario: components["schemas"]["Scenario"];
        };
        /** ScenarioVersionSummary */
        ScenarioVersionSummary: {
            /** Scenario Id */
            scenario_id: string;
            /** State Version */
            state_version: number;
            /** Name */
            name: string;
            /** Content Hash */
            content_hash: string;
            /** Created At */
            created_at: string | null;
            /** Data Origin */
            data_origin: string;
            /** Site Count */
            site_count: number;
            /** Cargo Count */
            cargo_count: number;
            /** Drone Count */
            drone_count: number;
            /** Battery Count */
            battery_count: number;
        };
        /** SchemaVersion */
        SchemaVersion: string;
        /** SimulationAction */
        SimulationAction: {
            /**
             * Action
             * @enum {string}
             */
            action: "start" | "pause" | "resume" | "speed" | "advance" | "disconnect" | "reconnect";
            /** Expected Revision */
            expected_revision: number;
            /** Idempotency Key */
            idempotency_key: string;
            /** Speed */
            speed?: number | null;
            /** Target Time S */
            target_time_s?: number | null;
        };
        /** Site */
        Site: {
            /** Id */
            id: string;
            /** Name */
            name: string;
            coordinates: components["schemas"]["Coordinates"];
            /** Ground Elevation M */
            ground_elevation_m: number | null;
            /** Available */
            available: boolean;
        };
        /** Snapshot */
        Snapshot: {
            /**
             * Schema Version
             * @constant
             */
            schema_version: "0.1.0-draft";
            /** Snapshot Id */
            snapshot_id: string;
            /** Scenario Id */
            scenario_id: string;
            /** Scenario State Version */
            scenario_state_version: number;
            /** Content Hash */
            content_hash: string;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            scenario: components["schemas"]["Scenario"];
        };
        /** SolveJob */
        SolveJob: {
            /**
             * Schema Version
             * @constant
             */
            schema_version: "0.1.0-draft";
            /** Job Id */
            job_id: string;
            /** Scenario Id */
            scenario_id: string;
            /** Snapshot Id */
            snapshot_id: string;
            /** Reserved Plan Id */
            reserved_plan_id: string;
            job_state: components["schemas"]["JobState"];
            solver_status: components["schemas"]["SolverStatus"] | null;
            /** Plan Id */
            plan_id: string | null;
            /** Has Validated Plan */
            has_validated_plan: boolean;
            /** Runtime S */
            runtime_s: number | null;
            /** Stop Reason */
            stop_reason: string | null;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Started At */
            started_at: string | null;
            /** Finished At */
            finished_at: string | null;
            error: components["schemas"]["Error1"] | null;
        };
        /** SolveRequest */
        SolveRequest: {
            /** Snapshot Id */
            snapshot_id: string;
            /**
             * Objective
             * @default time
             * @enum {string}
             */
            objective: "time" | "energy" | "balanced";
            /**
             * Objective Policy
             * @default deadline_first_v1
             * @enum {string}
             */
            objective_policy: "deadline_first_v1" | "tradeoff_v2";
            /**
             * Mode
             * @default quick
             * @enum {string}
             */
            mode: "quick" | "improve" | "replan";
            /**
             * Time Limit S
             * @default 15
             */
            time_limit_s: number;
            /**
             * Seed
             * @default 42
             */
            seed: number;
            /** Parent Plan Id */
            parent_plan_id?: string | null;
            /** Event Id */
            event_id?: string | null;
            /** Requested Model Scope */
            requested_model_scope?: string[];
            /**
             * Allow Partial Service
             * @default false
             * @constant
             */
            allow_partial_service: false;
            /** Initial Plan Id */
            initial_plan_id?: string | null;
            /** Repair Reference Id */
            repair_reference_id?: string | null;
            /** Engine Type */
            engine_type?: ("standard" | "eoh") | null;
            /** Heuristic Policy Id */
            heuristic_policy_id?: string | null;
            /** Heuristic Policy Sha256 */
            heuristic_policy_sha256?: string | null;
        };
        /** SolverNote */
        SolverNote: string;
        /**
         * SolverStatus
         * @enum {string}
         */
        SolverStatus: "OPTIMAL" | "FEASIBLE" | "INFEASIBLE" | "UNKNOWN" | "ERROR";
        /** Sortie */
        Sortie: {
            /** Sortie Id */
            sortie_id: string;
            /**
             * Kind
             * @constant
             */
            kind: "transport";
            /** Drone Id */
            drone_id: string;
            /** Battery Id */
            battery_id: string;
            /** Cargo Ids */
            cargo_ids: components["schemas"]["CargoId"][];
            /** Visits */
            visits: components["schemas"]["Visit"][];
            route_geometry: components["schemas"]["RouteGeometry1"];
            /** Prepare Start S */
            prepare_start_s: number;
            /** Takeoff S */
            takeoff_s: number;
            /** Return S */
            return_s: number;
            /** Drone Released S */
            drone_released_s: number;
            /** Battery Released S */
            battery_released_s: number;
            /** Energy Kwh */
            energy_kwh: number | null;
            /** Return Soc */
            return_soc: number | null;
            terrain_status: components["schemas"]["TerrainStatus"];
            communication_status: components["schemas"]["CommunicationStatus"];
            /** Charge Start S */
            charge_start_s?: number | null;
        };
        /** SortieLoad */
        SortieLoad: {
            /** Sortie Id */
            sortie_id: string;
            /** Drone Id */
            drone_id: string;
            /** Type Id */
            type_id: string;
            /** Cargo Count */
            cargo_count: number;
            /** Mass Kg */
            mass_kg: number;
            /** Volume L */
            volume_l: number;
            /** Max Payload Kg */
            max_payload_kg: number;
            /** Max Volume L */
            max_volume_l: number;
            /** Mass Utilization */
            mass_utilization: number;
            /** Volume Utilization */
            volume_utilization: number;
        };
        /**
         * Source
         * @enum {string}
         */
        Source: "gateway" | "relay";
        /** SourceReference */
        SourceReference: {
            /** Source Id */
            source_id: string;
            /** Name */
            name: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "project" | "terrain" | "weather" | "disaster";
            /** Url */
            url: string | null;
            /** Usage */
            usage: string;
            /** License Note */
            license_note: string;
        };
        /** Stage */
        Stage: {
            /** Stage */
            stage: string;
            /** Status */
            status: string;
            /** Seconds */
            seconds: number;
            /** Objective */
            objective: number | null;
        };
        /** StageAnalysis */
        StageAnalysis: {
            /** Plan Id */
            plan_id: string;
            /** Snapshot Id */
            snapshot_id: string;
            /**
             * Analysis Version
             * @default stages-v1
             * @constant
             */
            analysis_version: "stages-v1";
            /**
             * Position Semantics
             * @default model_phase_geodesic
             * @constant
             */
            position_semantics: "model_phase_geodesic";
            /**
             * Soc Semantics
             * @default computed_phase_endpoints_only
             * @constant
             */
            soc_semantics: "computed_phase_endpoints_only";
            /** Trajectory Segments */
            trajectory_segments: components["schemas"]["TrajectorySegment"][];
            /** Sortie Loads */
            sortie_loads?: components["schemas"]["SortieLoad"][];
        };
        /** StationCoordinate */
        StationCoordinate: number;
        /** StationCoordinate1 */
        StationCoordinate1: number;
        /**
         * Status
         * @enum {string}
         */
        Status: "passed" | "failed" | "partial" | "not_run";
        /**
         * Status1
         * @enum {string}
         */
        Status1: "passed" | "failed" | "not_evaluated";
        /**
         * Status2
         * @enum {string}
         */
        Status2: "available" | "unavailable";
        /**
         * Status3
         * @enum {string}
         */
        Status3: "available" | "charging" | "unavailable";
        /**
         * Status4
         * @enum {string}
         */
        Status4: "not_evaluated" | "available" | "invalid";
        /**
         * Status5
         * @enum {string}
         */
        Status5: "available" | "reserved" | "loaded" | "in_transit" | "delivered" | "unavailable";
        /**
         * Status6
         * @enum {string}
         */
        Status6: "available" | "reserved" | "loaded" | "in_flight" | "unavailable";
        /**
         * Status7
         * @enum {string}
         */
        Status7: "available" | "reserved" | "in_use" | "charging" | "unavailable";
        /**
         * Status8
         * @enum {string}
         */
        Status8: "available" | "reserved" | "loaded" | "in_transit" | "delivered" | "unavailable";
        /** SupportedChargeModel */
        SupportedChargeModel: string;
        /** SupportedEnergyModel */
        SupportedEnergyModel: string;
        /** SupportedEvent */
        SupportedEvent: string;
        /**
         * SupportedModelScopeEnum
         * @enum {string}
         */
        SupportedModelScopeEnum: "cargo_unique" | "capacity" | "inventory" | "aircraft" | "battery" | "time_window" | "energy" | "terrain" | "communication" | "restricted_zone" | "ground_resource" | "weather_window";
        /**
         * SupportedObjective
         * @enum {string}
         */
        SupportedObjective: "time" | "energy" | "balanced";
        /** TelemetrySample */
        TelemetrySample: {
            /** Device Id */
            device_id: string;
            /** Device Session Id */
            device_session_id: string;
            /** Device Sequence */
            device_sequence: number;
            /**
             * Observed At
             * Format: date-time
             */
            observed_at: string;
            /**
             * Received At
             * Format: date-time
             */
            received_at: string;
            /** Time S */
            time_s: number;
            /** Coordinates */
            coordinates: [
                number,
                number
            ] | null;
            /** Elevation M */
            elevation_m: number | null;
            /** Vertical Datum */
            vertical_datum: string | null;
            /** Soc */
            soc: number | null;
            /** Soc Sample Time S */
            soc_sample_time_s: number | null;
            /** Model Horizontal Speed Mps */
            model_horizontal_speed_mps?: number | null;
            /** Model Vertical Speed Mps */
            model_vertical_speed_mps?: number | null;
            /** Estimated Soc */
            estimated_soc?: number | null;
            /** Payload Kg */
            payload_kg?: number | null;
            /** Phase End S */
            phase_end_s?: number | null;
            /** Phase */
            phase: string;
            /** Availability */
            availability?: ("available" | "not_ready" | "unavailable") | null;
            /** Availability Reason */
            availability_reason?: string | null;
            /** Sortie Id */
            sortie_id: string | null;
            /** Battery Id */
            battery_id?: string | null;
            /** Component Id */
            component_id?: string | null;
            /** Cargo Ids */
            cargo_ids: string[];
            /**
             * Quality
             * @enum {string}
             */
            quality: "simulated" | "stale" | "missing";
            /** Active Plan Id */
            active_plan_id: string;
        };
        /** Terrain */
        Terrain: {
            status: components["schemas"]["Status4"];
            /** Asset Id */
            asset_id: string | null;
            /** Sha256 */
            sha256: string | null;
            /** Horizontal Crs */
            horizontal_crs: string | null;
            /** Vertical Datum */
            vertical_datum: string | null;
        };
        /** TerrainAsset */
        TerrainAsset: {
            /** Asset Id */
            asset_id: string;
            /** Name */
            name: string;
            /** Sha256 */
            sha256: string;
            terrain: components["schemas"]["Terrain"];
            /** Bounds */
            bounds: [
                number,
                number,
                number,
                number
            ];
            /** Dimensions */
            dimensions: [
                number,
                number
            ];
            /** Valid Fraction */
            valid_fraction: number;
            /** Source Sha256 */
            source_sha256: string | null;
            /** Source Crs */
            source_crs: string;
            /** Processing */
            processing: string[];
        };
        /** TerrainAssignment */
        TerrainAssignment: {
            /** Expected State Version */
            expected_state_version: number;
            /** Asset Id */
            asset_id: string;
            /** Sha256 */
            sha256: string;
            /**
             * Update Dem Elevations
             * @default true
             */
            update_dem_elevations: boolean;
        };
        /** TerrainMap */
        TerrainMap: {
            /** Asset Id */
            asset_id: string;
            /** Name */
            name: string;
            /** Sha256 */
            sha256: string;
            /** Bounds */
            bounds: [
                number,
                number,
                number,
                number
            ];
            /** Coordinates */
            coordinates: [
                [
                    number,
                    number
                ],
                [
                    number,
                    number
                ],
                [
                    number,
                    number
                ],
                [
                    number,
                    number
                ]
            ];
            /** Crs */
            crs: string;
            /** Source */
            source: string;
            /** Notice */
            notice: string;
            /** Image Url */
            image_url: string;
        };
        /**
         * TerrainStatus
         * @enum {string}
         */
        TerrainStatus: "passed" | "failed" | "not_evaluated";
        /** TerrainSurface */
        TerrainSurface: {
            /** Asset Id */
            asset_id: string;
            /** Name */
            name: string;
            /** Sha256 */
            sha256: string;
            /** Bounds */
            bounds: [
                number,
                number,
                number,
                number
            ];
            /** Longitude */
            longitude: number[];
            /** Latitude */
            latitude: number[];
            /** Elevations M */
            elevations_m: (number | null)[][];
            /** Min Elevation M */
            min_elevation_m: number;
            /** Max Elevation M */
            max_elevation_m: number;
            /** Valid Fraction */
            valid_fraction: number;
            /** Notice */
            notice: string;
        };
        /** TrajectorySegment */
        TrajectorySegment: {
            /** Sortie Id */
            sortie_id: string;
            /** Drone Id */
            drone_id: string;
            /** Phase Id */
            phase_id: string;
            /**
             * Phase
             * @enum {string}
             */
            phase: "prepare" | "climb" | "cruise" | "descent" | "handover" | "turnaround" | "charge_wait" | "charge" | "relay_link" | "relay_service";
            /** Start S */
            start_s: number;
            /** End S */
            end_s: number;
            /** From Coordinates */
            from_coordinates: [
                number,
                number
            ];
            /** To Coordinates */
            to_coordinates: [
                number,
                number
            ];
            /** Start Elevation M */
            start_elevation_m: number | null;
            /** End Elevation M */
            end_elevation_m: number | null;
            /** Vertical Datum */
            vertical_datum: string | null;
            /** Payload Kg */
            payload_kg: number;
            /** Energy Kwh */
            energy_kwh: number;
            /** Soc Start */
            soc_start: number | null;
            /** Soc End */
            soc_end: number | null;
            /** Cargo Ids */
            cargo_ids: string[];
        };
        /** UnservedDemandId */
        UnservedDemandId: string;
        /** Validation */
        Validation: {
            status: components["schemas"]["Status"];
            /** Checks */
            checks: components["schemas"]["Check"][];
        };
        /** ValidationError */
        ValidationError: {
            /** Location */
            loc: (string | number)[];
            /** Message */
            msg: string;
            /** Error Type */
            type: string;
            /** Input */
            input?: unknown;
            /** Context */
            ctx?: Record<string, never>;
        };
        /** VersionRequest */
        VersionRequest: {
            /** Expected State Version */
            expected_state_version: number;
        };
        /** Visit */
        Visit: {
            /** Site Id */
            site_id: string;
            /** Cargo Ids */
            cargo_ids: components["schemas"]["CargoId"][];
            /** Delivery Complete S */
            delivery_complete_s: number;
        };
        /** Weather */
        Weather: {
            /**
             * Model Id
             * @constant
             */
            model_id: "manual_operating_window_v1";
            /** Weather Id */
            weather_id: string;
            /**
             * Source Kind
             * @constant
             */
            source_kind: "manual_scenario";
            /** Source Ref */
            source_ref: string;
            /**
             * Issued At
             * Format: date-time
             */
            issued_at: string;
            /** Valid From S */
            valid_from_s: number;
            /** Valid Until S */
            valid_until_s: number;
            /** Height M */
            height_m: number;
            /**
             * Height Reference
             * @constant
             */
            height_reference: "AGL";
            /** Wind Speed Mps */
            wind_speed_mps: number | null;
            /** Gust Mps */
            gust_mps: number | null;
            /** Wind Direction From Deg */
            wind_direction_from_deg: number | null;
            /** Temperature C */
            temperature_c: number | null;
            /** Precipitation Mm H */
            precipitation_mm_h: number | null;
            /** Rules */
            rules: components["schemas"]["WeatherRule"][];
        };
        /** WeatherRule */
        WeatherRule: {
            /** Type Id */
            type_id: string;
            /** Source Ref */
            source_ref: string;
            /** Max Wind Mps */
            max_wind_mps: number | null;
            /** Max Gust Mps */
            max_gust_mps: number | null;
            /** Min Temperature C */
            min_temperature_c: number | null;
            /** Max Temperature C */
            max_temperature_c: number | null;
            /** Max Precipitation Mm H */
            max_precipitation_mm_h: number | null;
        };
        /** WhatIfHistory */
        WhatIfHistory: {
            /** Scenario Id */
            scenario_id: string;
            /** Name */
            name: string;
            /** Scenario State Version */
            scenario_state_version: number;
            origin: components["schemas"]["ScenarioOrigin"];
            job: components["schemas"]["SolveJob"] | null;
            plan: components["schemas"]["Plan"] | null;
        };
        /** WhatIfReceipt */
        WhatIfReceipt: {
            scenario: components["schemas"]["Scenario"];
            origin: components["schemas"]["ScenarioOrigin"];
        };
        /** WhatIfRequest */
        WhatIfRequest: {
            /** Expected State Version */
            expected_state_version: number;
            /** Source Plan Id */
            source_plan_id?: string | null;
            /**
             * Name
             * @default 资源与余量试算
             */
            name: string;
            /** Additions */
            additions?: components["schemas"]["ResourceAddition"][];
            ground_addition?: components["schemas"]["GroundResourceAddition"] | null;
            /**
             * Energy Multiplier
             * @default 1
             */
            energy_multiplier: number;
            /**
             * Flight Time Multiplier
             * @default 1
             */
            flight_time_multiplier: number;
            /**
             * Battery Soh Multiplier
             * @default 1
             */
            battery_soh_multiplier: number;
            /** Min Return Soc */
            min_return_soc?: number | null;
            /**
             * Noncritical Deadline Multiplier
             * @default 1
             */
            noncritical_deadline_multiplier: number;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    health_api_v1_health_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Health"];
                };
            };
        };
    };
    meta_api_v1_meta_capabilities_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Capabilities"];
                };
            };
        };
    };
    map_terrain_api_v1_map_terrain_get: {
        parameters: {
            query?: {
                asset_id?: string | null;
                sha256?: string | null;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TerrainMap"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    bound_terrain_image_api_v1_map_terrain__asset_id___sha256__png_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                asset_id: string;
                sha256: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    map_surface_api_v1_map_surface_get: {
        parameters: {
            query: {
                asset_id: string;
                sha256: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TerrainSurface"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    map_terrain_image_api_v1_map_terrain_png_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    scenario_versions_api_v1_scenarios__scenario_id__versions_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ScenarioVersionSummary"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    scenario_version_api_v1_scenarios__scenario_id__versions__version__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
                version: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Scenario"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_scenarios_api_v1_scenarios_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ScenarioSummary"][];
                };
            };
        };
    };
    list_terrain_assets_api_v1_terrain_assets_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TerrainAsset"][];
                };
            };
        };
    };
    upload_terrain_api_v1_terrain_assets_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "multipart/form-data": components["schemas"]["Body_upload_terrain_api_v1_terrain_assets_post"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TerrainAsset"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    download_terrain_api_v1_terrain_assets__asset_id__source_get: {
        parameters: {
            query: {
                sha256: string;
            };
            header?: never;
            path: {
                asset_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    download_terrain_package_api_v1_terrain_assets__asset_id__package_get: {
        parameters: {
            query: {
                sha256: string;
            };
            header?: never;
            path: {
                asset_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    upload_terrain_package_api_v1_terrain_assets_import_package_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "multipart/form-data": components["schemas"]["Body_upload_terrain_package_api_v1_terrain_assets_import_package_post"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TerrainAsset"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    assign_terrain_api_v1_scenarios__scenario_id__terrain_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TerrainAssignment"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Scenario"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    load_example_api_v1_scenarios_examples_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ExampleRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Scenario"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    import_scenario_api_v1_scenarios_import_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["Scenario"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Scenario"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    communication_template_api_v1_scenarios__scenario_id__communication_template_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Communication"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    plan_playback_api_v1_plans__plan_id__playback_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                plan_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Playback"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    plan_analysis_api_v1_plans__plan_id__analysis_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                plan_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PlanAnalysis"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    plan_flight_profile_api_v1_plans__plan_id__flight_profile_get: {
        parameters: {
            query: {
                sortie_id: string;
            };
            header?: never;
            path: {
                plan_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["FlightProfile"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    plan_partition_api_v1_plans__plan_id__partition_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                plan_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PartitionReport"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    plan_radio_coverage_api_v1_plans__plan_id__radio_coverage_get: {
        parameters: {
            query?: {
                altitude_agl_m?: number;
                relay_sortie_id?: string | null;
                grid_size?: number;
            };
            header?: never;
            path: {
                plan_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RadioCoverage"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    plan_report_api_v1_plans__plan_id__report_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                plan_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "text/html": string;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    what_if_history_api_v1_scenarios__scenario_id__what_if_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["WhatIfHistory"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    what_if_api_v1_scenarios__scenario_id__what_if_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["WhatIfRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["WhatIfReceipt"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    scenario_origin_api_v1_scenarios__scenario_id__origin_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ScenarioOrigin"] | null;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    import_file_api_v1_scenarios_import_file_post: {
        parameters: {
            query?: {
                scenario_id?: string | null;
                entity?: string | null;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "multipart/form-data": components["schemas"]["Body_import_file_api_v1_scenarios_import_file_post"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ImportPreview"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    template_api_v1_scenarios__scenario_id__template_get: {
        parameters: {
            query?: {
                format?: "csv" | "xlsx";
                entity?: string;
            };
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_scenario_api_v1_scenarios__scenario_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Scenario"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_scenario_api_v1_scenarios__scenario_id__put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ScenarioUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Scenario"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    copy_scenario_api_v1_scenarios__scenario_id__copy_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CopyRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Scenario"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    validate_input_api_v1_scenarios__scenario_id__validate_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["VersionRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Validation"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    make_snapshot_api_v1_scenarios__scenario_id__snapshots_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["VersionRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Snapshot"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_snapshot_api_v1_snapshots__snapshot_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                snapshot_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Snapshot"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    single_site_analysis_api_v1_snapshots__snapshot_id__single_site_analysis_get: {
        parameters: {
            query?: {
                min_return_soc?: number | null;
            };
            header?: never;
            path: {
                snapshot_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["NominalReport"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_job_api_v1_solve_jobs_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SolveRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SolveJob"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_job_api_v1_solve_jobs__job_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SolveJob"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    scenario_jobs_api_v1_scenarios__scenario_id__solve_jobs_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SolveJob"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_progress_api_v1_solve_jobs__job_id__progress_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Progress"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_job_diagnostics_api_v1_solve_jobs__job_id__diagnostics_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    cancel_job_api_v1_solve_jobs__job_id__cancel_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SolveJob"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_plans_api_v1_scenarios__scenario_id__plans_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PlanSummary"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_plan_api_v1_plans__plan_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                plan_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Plan"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    compare_api_v1_plans__plan_id__comparison_get: {
        parameters: {
            query: {
                other_plan_id: string;
            };
            header?: never;
            path: {
                plan_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Comparison"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    confirm_api_v1_plans__plan_id__confirm_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                plan_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConfirmRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Confirmation"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    apply_event_api_v1_events_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["Event"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EventReceipt"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_events_api_v1_scenarios__scenario_id__events_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Event"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    export_plan_api_v1_plans__plan_id__export_get: {
        parameters: {
            query?: {
                format?: "json" | "csv" | "geojson" | "relay_csv" | "xlsx";
            };
            header?: never;
            path: {
                plan_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    export_scenario_api_v1_scenarios__scenario_id__export_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Scenario"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    export_bundle_api_v1_scenarios__scenario_id__bundle_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scenario_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    input_preview_api_v1_missions__mission_id__input_preview_post: {
        parameters: {
            query?: {
                entity?: string;
            };
            header?: never;
            path: {
                mission_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "multipart/form-data": components["schemas"]["Body_input_preview_api_v1_missions__mission_id__input_preview_post"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DraftImportPreview"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    input_template_api_v1_missions__mission_id__input_template_get: {
        parameters: {
            query?: {
                entity?: string;
                format?: string;
            };
            header?: never;
            path: {
                mission_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_missions_api_v1_missions_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MissionView"][];
                };
            };
        };
    };
    create_mission_api_v1_missions_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MissionCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MissionView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_mission_api_v1_missions__mission_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                mission_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MissionView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_mission_api_v1_missions__mission_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                mission_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MissionUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MissionView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_draft_api_v1_missions__mission_id__draft_put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                mission_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MissionDraftUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MissionView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    clone_mission_api_v1_missions__mission_id__clone_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                mission_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MissionCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MissionView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    preflight_api_v1_missions__mission_id__preflight_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                mission_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PreflightRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PreflightReport"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_report_api_v1_preflight_reports__report_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                report_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PreflightReport"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_reports_api_v1_missions__mission_id__preflight_reports_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                mission_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PreflightReport"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    stages_api_v1_plans__plan_id__stages_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                plan_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["StageAnalysis"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    cases_api_v1_case_library_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseCatalog"];
                };
            };
        };
    };
    preview_api_v1_case_library__case_id__preview_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Scenario"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    heuristic_packages_api_v1_heuristic_packages_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HeuristicPackage"][];
                };
            };
        };
    };
    export_policy_api_v1_heuristic_packages__policy_id__export_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                policy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    import_policy_api_v1_heuristic_packages_import_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "multipart/form-data": components["schemas"]["Body_import_policy_api_v1_heuristic_packages_import_post"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HeuristicPackage"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    overview_api_v1_asset_overview_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AssetOverview"];
                };
            };
        };
    };
    overview_api_v1_integrations_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["IntegrationOverview"];
                };
            };
        };
    };
    configuration_api_v1_integrations_configuration_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    operation_capabilities_api_v1_meta_operations_capabilities_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["OperationCapabilities"];
                };
            };
        };
    };
    device_mission_state_api_v1_executions__execution_id__devices__device_id__mission_state_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                execution_id: string;
                device_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DeviceMissionState"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_execution_api_v1_executions_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ExecutionCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExecutionView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_executions_api_v1_missions__mission_id__executions_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                mission_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExecutionView"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_execution_api_v1_executions__execution_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                execution_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExecutionView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    action_api_v1_executions__execution_id__simulation_actions_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                execution_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SimulationAction"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExecutionView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_events_api_v1_executions__execution_id__events_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                execution_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExecutionEventView"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    event_api_v1_executions__execution_id__events_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                execution_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ExecutionEventInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExecutionEventView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    resolve_event_api_v1_executions__execution_id__events__event_id__resolve_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                execution_id: string;
                event_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EventResolution"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExecutionEventView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    repair_api_v1_executions__execution_id__replan_jobs_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                execution_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RepairRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RepairView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_changes_api_v1_executions__execution_id__plan_changes_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                execution_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RepairView"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_change_api_v1_executions__execution_id__plan_changes__change_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                execution_id: string;
                change_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RepairView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    apply_change_api_v1_executions__execution_id__plan_changes__change_id__apply_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                execution_id: string;
                change_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ApplyRepair"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RepairView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    device_capabilities_api_v1_devices__device_id__capabilities_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                device_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DeviceCapabilities"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    command_api_v1_commands_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CommandRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommandView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_command_api_v1_commands__command_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                command_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommandView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    analysis_api_v1_executions__execution_id__analysis_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                execution_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExecutionAnalysis"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    stream_api_v1_executions__execution_id__stream_get: {
        parameters: {
            query?: {
                cursor?: number;
            };
            header?: never;
            path: {
                execution_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    export_execution_api_v1_executions__execution_id__export_get: {
        parameters: {
            query?: {
                version?: number;
            };
            header?: never;
            path: {
                execution_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    import_archive_api_v1_execution_archives_import_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "multipart/form-data": components["schemas"]["Body_import_archive_api_v1_execution_archives_import_post"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExecutionArchiveSummary"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_archives_api_v1_execution_archives_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExecutionArchiveSummary"][];
                };
            };
        };
    };
    get_archive_api_v1_execution_archives__archive_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                archive_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExecutionArchiveView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_experiments_api_v1_experiments_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExperimentView"][];
                };
            };
        };
    };
    create_experiment_api_v1_experiments_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ExperimentRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExperimentView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_experiment_api_v1_experiments__experiment_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                experiment_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExperimentView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    cancel_experiment_api_v1_experiments__experiment_id__cancel_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                experiment_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExperimentView"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    export_experiment_api_v1_experiments__experiment_id__export_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                experiment_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExperimentBundle"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
}
