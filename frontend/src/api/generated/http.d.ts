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
            status: components["schemas"]["Status5"];
            /** Location Id */
            location_id: string;
            /** Available After S */
            available_after_s: number;
        };
        /** Body_import_file_api_v1_scenarios_import_file_post */
        Body_import_file_api_v1_scenarios_import_file_post: {
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
            status: components["schemas"]["Status3"];
            /** Location Id */
            location_id: string;
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
        /**
         * Code
         * @enum {string}
         */
        Code: "cargo_unique" | "capacity" | "inventory" | "aircraft" | "battery" | "time_window" | "energy" | "terrain" | "communication" | "restricted_zone";
        /**
         * Code1
         * @enum {string}
         */
        Code1: "SCHEMA_INVALID" | "REFERENCE_INVALID" | "RESOURCE_CONFLICT" | "STATE_VERSION_CONFLICT" | "SNAPSHOT_STALE" | "UNSUPPORTED_SCOPE" | "INPUT_NOT_READY" | "NO_VALIDATED_PLAN" | "UNSUPPORTED_EVENT_STATE" | "SOLVER_BUSY" | "CANCELED" | "EXTERNAL_ASSET_UNAVAILABLE" | "INTERNAL_ERROR";
        /**
         * CommunicationStatus
         * @enum {string}
         */
        CommunicationStatus: "passed" | "failed" | "not_evaluated";
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
        Coordinate2: components["schemas"]["Coordinates"][];
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
        /** Drone */
        Drone: {
            /** Drone Id */
            drone_id: string;
            /** Type Id */
            type_id: string;
            status: components["schemas"]["Status4"];
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
        /** EnergyModel */
        EnergyModel: {
            /** Model Id */
            model_id: string;
            /** Parameters */
            parameters: {
                [key: string]: number;
            };
        };
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
        /** Event */
        Event: {
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
        /** EventReceipt */
        EventReceipt: {
            event: components["schemas"]["Event"];
            /** State Version After */
            state_version_after: number;
            /** Applied */
            applied: boolean;
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
        /** Geometry */
        Geometry: {
            /**
             * Type
             * @constant
             */
            type: "Polygon";
            /** Coordinates */
            coordinates: components["schemas"]["Coordinate2"][];
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
        /**
         * JobState
         * @enum {string}
         */
        JobState: "queued" | "running" | "completed" | "failed" | "canceled";
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
        /**
         * Mode
         * @enum {string}
         */
        Mode: "simulation" | "planning_assist";
        /**
         * ModelScopeEnum
         * @enum {string}
         */
        ModelScopeEnum: "cargo_unique" | "capacity" | "inventory" | "aircraft" | "battery" | "time_window" | "energy" | "terrain" | "communication" | "restricted_zone";
        /**
         * Objective
         * @enum {string}
         */
        Objective: "time" | "energy" | "balanced";
        /** Payload */
        Payload: {
            /** Drone Id */
            drone_id: string;
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
        /** RemovedSortieId */
        RemovedSortieId: string;
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
        /** ResourceUsage */
        ResourceUsage: {
            /**
             * Kind
             * @enum {string}
             */
            kind: "drone" | "battery";
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
             * @constant
             */
            transformation_version: "what_if_v1";
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
        /** SchemaVersion */
        SchemaVersion: string;
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
            route_geometry: components["schemas"]["RouteGeometry"];
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
        };
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
        Status2: "not_evaluated" | "available" | "invalid";
        /**
         * Status3
         * @enum {string}
         */
        Status3: "available" | "reserved" | "loaded" | "in_transit" | "delivered" | "unavailable";
        /**
         * Status4
         * @enum {string}
         */
        Status4: "available" | "reserved" | "loaded" | "in_flight" | "unavailable";
        /**
         * Status5
         * @enum {string}
         */
        Status5: "available" | "reserved" | "in_use" | "charging" | "unavailable";
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
        SupportedModelScopeEnum: "cargo_unique" | "capacity" | "inventory" | "aircraft" | "battery" | "time_window" | "energy" | "terrain" | "communication" | "restricted_zone";
        /**
         * SupportedObjective
         * @enum {string}
         */
        SupportedObjective: "time" | "energy" | "balanced";
        /** Terrain */
        Terrain: {
            status: components["schemas"]["Status2"];
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
                format?: "json" | "csv" | "geojson";
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
}
