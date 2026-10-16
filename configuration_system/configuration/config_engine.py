from .knowledge import (
    get_requirement_by_name,
    get_parameters_for_requirements,
)

from .models import (
    ProjectInput,
    ProjectInfo,
    ConfigurationMapping,
    ConfigurationParameter,
    ConfigurationSummary,
    ConfigurationOutput,
)


def generate_configuration(
    project_input: ProjectInput
) -> ConfigurationOutput:
    """
    Generate a deterministic configuration from
    structured project requirements.

    DEFAULT is automatically included.
    """

    # ------------------------------------------------------------
    # Get selected requirements
    # ------------------------------------------------------------

    selected_requirements = list(
        project_input.requirements
    )

    # DEFAULT is always required
    if "DEFAULT" not in selected_requirements:
        selected_requirements.insert(
            0,
            "DEFAULT"
        )

    # ------------------------------------------------------------
    # Validate requirements
    # ------------------------------------------------------------

    validated_requirements = []

    for requirement_name in selected_requirements:

        requirement = get_requirement_by_name(
            requirement_name
        )

        if requirement is None:
            raise ValueError(
                f"Unknown requirement: {requirement_name}"
            )

        validated_requirements.append(
            requirement
        )

    # ------------------------------------------------------------
    # Retrieve parameters from Knowledge Base
    # ------------------------------------------------------------

    raw_parameters = get_parameters_for_requirements(
        selected_requirements
    )

    # ------------------------------------------------------------
    # Convert database dictionaries into
    # ConfigurationParameter objects
    # ------------------------------------------------------------

    parameters = []

    for parameter in raw_parameters:

        mappings = []

        for mapping in parameter["mappings"]:

            mappings.append(
                ConfigurationMapping(
                    access_type=mapping[
                        "access_type"
                    ],
                    plc_parameter_name=mapping[
                        "plc_parameter_name"
                    ],
                    pc_parameter_name=mapping[
                        "pc_parameter_name"
                    ],
                )
            )

        configuration_parameter = (
            ConfigurationParameter(
                id=parameter["id"],
                name=parameter["name"],
                data_type=parameter[
                    "data_type"
                ],
                description=parameter[
                    "description"
                ],
                source_requirements=parameter[
                    "requirements"
                ],
                mappings=mappings,
            )
        )

        parameters.append(
            configuration_parameter
        )

    # ------------------------------------------------------------
    # Build summary
    # ------------------------------------------------------------

    summary = ConfigurationSummary(
        requirements_count=len(
            validated_requirements
        ),
        parameters_count=len(
            parameters
        ),
    )

    # ------------------------------------------------------------
    # Final configuration
    # ------------------------------------------------------------

    return ConfigurationOutput(
        project=project_input.project,
        requirements=[
            requirement["name"]
            for requirement in validated_requirements
        ],
        parameters=parameters,
        summary=summary,
    )