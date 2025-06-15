from typing import Dict, Any, List
import json
from pydantic import BaseModel
from api.services.ai_service import ContractStructure
import openai
from api.core.config import settings

class VisualizationService:
    """Service for generating visualizations of smart contracts"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_visualization(
            self,
            contract_structure: ContractStructure,
            visualization_type: str = "flowchart"
    ) -> Dict[str, Any]:
        """
        Generate visualization data based on contract structure

        Args:
            contract_structure: Parsed structure of the smart contract
            visualization_type: Type of visualization to generate (flowchart, sequence, etc.)

        Returns:
            Dictionary with visualization data that can be rendered on the frontend
        """
        if visualization_type == "flowchart":
            return self._generate_flowchart(contract_structure)
        elif visualization_type == "sequence":
            return self._generate_sequence_diagram(contract_structure)
        elif visualization_type == "interaction":
            return self._generate_interaction_diagram(contract_structure)
        else:
            # Default to flowchart
            return self._generate_flowchart(contract_structure)

    def _generate_flowchart(self, contract_structure: ContractStructure) -> Dict[str, Any]:
        """Generate a flowchart visualization of the contract"""

        # Extract key components for visualization
        functions = contract_structure.functions
        variables = contract_structure.variables
        events = contract_structure.events

        # Generate nodes for the flowchart
        nodes: List[Dict[str, Any]] = []

        # Contract node (center)
        nodes.append({
            "id": "contract",
            "type": "contract",
            "data": {
                "label": contract_structure.summary.get("contractName", "Contract"),
                "description": contract_structure.summary.get("description", ""),
            },
            "position": {"x": 0, "y": 0}
        })

        # Function nodes
        for i, func in enumerate(functions):
            angle = (2 * 3.14159 * i) / len(functions) if functions else 0
            radius = 200

            # Simple positioning in a circle around the contract
            x = radius * (i % 2 * 2 - 1)  # Alternate left and right
            y = 100 + 80 * (i // 2)  # Stack vertically with spacing

            nodes.append({
                "id": f"function_{func['name']}",
                "type": "function",
                "data": {
                    "label": func["name"],
                    "visibility": func.get("visibility", "unknown"),
                    "modifiers": func.get("modifiers", []),
                    "parameters": func.get("parameters", []),
                    "returns": func.get("returns", []),
                    "description": func.get("description", "")
                },
                "position": {"x": x, "y": y}
            })

        # Generate edges (connections between nodes)
        edges: List[Dict[str, Any]] = []

        # Connect contract to all functions
        for func in functions:
            edges.append({
                "id": f"edge_contract_to_{func['name']}",
                "source": "contract",
                "target": f"function_{func['name']}",
                "type": "function_call"
            })

        # Connect functions to events they emit
        for func in functions:
            func_name = func["name"]
            # This is a simplification - in a real system, you'd analyze the function code
            # to determine which events it emits
            for event in events:
                event_name = event["name"]
                if any(event_name.lower() in line.lower() for line in func.get("description", "").split(".")):
                    edges.append({
                        "id": f"edge_{func_name}_to_{event_name}",
                        "source": f"function_{func_name}",
                        "target": f"event_{event_name}",
                        "type": "event_emission"
                    })

        # Generate Mermaid flowchart syntax
        mermaid_code = self._generate_mermaid_flowchart(contract_structure)

        return {
            "type": "flowchart",
            "nodes": nodes,
            "edges": edges,
            "mermaid": mermaid_code
        }

    def _generate_sequence_diagram(self, contract_structure: ContractStructure) -> Dict[str, Any]:
        """Generate a sequence diagram visualization showing the typical flow of contract execution"""

        # For the sequence diagram, we'll generate a Mermaid diagram that shows
        # how the contract might be used in a typical scenario

        # Extract main actors and functions
        contract_name = contract_structure.summary.get("contractName", "Contract")
        main_functions = [f for f in contract_structure.functions
                          if f.get("visibility") in ["public", "external"]]

        # Create sequence diagram nodes
        actors = ["User", contract_name, "Blockchain"]

        # Create sequence of actions based on the data flow description
        data_flow = contract_structure.summary.get("data_flow", [])
        if not data_flow:
            # If no explicit data flow, create a simple one based on functions
            data_flow = [f"User calls {func['name']}" for func in main_functions[:3]]

        # Convert to mermaid syntax
        mermaid_code = self._generate_mermaid_sequence(
            actors=actors,
            contract_name=contract_name,
            data_flow=data_flow,
            functions=main_functions
        )

        return {
            "type": "sequence",
            "actors": actors,
            "interactions": data_flow,
            "mermaid": mermaid_code
        }

    def _generate_interaction_diagram(self, contract_structure: ContractStructure) -> Dict[str, Any]:
        """Generate an interactive diagram showing how users can interact with the contract"""

        # This would be a more complex diagram showing the possible user interactions
        contract_name = contract_structure.summary.get("contractName", "Contract")
        functions = contract_structure.functions

        # Use AI to generate potential user stories/interactions
        user_interactions = self._generate_user_interactions(contract_structure)

        # Generate visualization data
        return {
            "type": "interaction",
            "contract_name": contract_name,
            "user_interactions": user_interactions,
            "functions": [f["name"] for f in functions if f.get("visibility") in ["public", "external"]]
        }

    def _generate_mermaid_flowchart(self, contract_structure: ContractStructure) -> str:
        """Generate Mermaid syntax for a flowchart diagram"""

        contract_name = contract_structure.summary.get("contractName", "Contract")
        functions = contract_structure.functions
        events = contract_structure.events

        mermaid_lines = [
            "flowchart TD",
            f"    Contract[{contract_name}]"
        ]

        # Add function nodes
        for func in functions:
            func_name = func["name"]
            visibility = func.get("visibility", "")
            modifier_text = " ".join(func.get("modifiers", []))

            # Use different shapes for different visibility
            shape = ")" if visibility == "external" else "(" if visibility == "public" else "["
            end_shape = ")" if visibility == "external" else ")" if visibility == "public" else "]"

            # Add modifiers as text if present
            modifier_display = f"\\n{modifier_text}" if modifier_text else ""

            mermaid_lines.append(f"    {func_name}{shape}{func_name}{modifier_display}{end_shape}")
            mermaid_lines.append(f"    Contract --> {func_name}")

        # Add event nodes
        for event in events:
            event_name = event["name"]
            mermaid_lines.append(f"    Event_{event_name}[/{event_name}/]")

            # Connect functions to events (simplified)
            for func in functions:
                if any(event_name.lower() in line.lower() for line in func.get("description", "").split(".")):
                    mermaid_lines.append(f"    {func['name']} -.-> Event_{event_name}")

        return "\n".join(mermaid_lines)

    def _generate_mermaid_sequence(
            self,
            actors: List[str],
            contract_name: str,
            data_flow: List[str],
            functions: List[Dict[str, Any]]
    ) -> str:
        """Generate Mermaid syntax for a sequence diagram"""

        mermaid_lines = [
            "sequenceDiagram",
            "    participant U as User",
            f"    participant C as {contract_name}",
            "    participant B as Blockchain"
        ]

        # Add sequence based on data flow
        for i, step in enumerate(data_flow):
            step_lower = step.lower()

            if "call" in step_lower:
                # User calling contract function
                for func in functions:
                    if func["name"].lower() in step_lower:
                        mermaid_lines.append(f"    U->>C: {func['name']}()")

                        # If function modifies state, show interaction with blockchain
                        if any(mod in ["payable", "nonReentrant"] for mod in func.get("modifiers", [])):
                            mermaid_lines.append(f"    C->>B: Update state")
                            mermaid_lines.append(f"    B-->>C: Confirmation")

                        # Show return to user
                        mermaid_lines.append(f"    C-->>U: Return result")
                        break
            elif "emit" in step_lower or "event" in step_lower:
                # Contract emitting an event
                mermaid_lines.append(f"    C->>B: Emit event")
            elif "check" in step_lower or "verify" in step_lower:
                # Contract checking something
                mermaid_lines.append(f"    C->>C: Internal validation")
            else:
                # Generic interaction if we can't determine the type
                mermaid_lines.append(f"    U->>C: Interaction {i+1}")
                mermaid_lines.append(f"    C-->>U: Response")

        return "\n".join(mermaid_lines)

    def _generate_user_interactions(self, contract_structure: ContractStructure) -> List[Dict[str, Any]]:
        """
        Use the AI to generate realistic user interaction scenarios with the contract
        """
        contract_summary = json.dumps(contract_structure.summary)
        functions_json = json.dumps([
            {
                "name": f["name"],
                "visibility": f.get("visibility", ""),
                "modifiers": f.get("modifiers", []),
                "parameters": f.get("parameters", []),
                "description": f.get("description", "")
            }
            for f in contract_structure.functions
            if f.get("visibility") in ["public", "external"]
        ])

        prompt = f"""
        Based on this smart contract structure, generate 3-5 typical user interaction scenarios.
        Each scenario should represent a realistic way a user might interact with this contract.
        
        Contract summary: {contract_summary}
        
        Available public/external functions:
        {functions_json}
        
        For each scenario, provide:
        1. A name for the scenario
        2. A brief description of what the user is trying to achieve
        3. A sequence of 2-5 steps showing the interactions with the contract
        
        Format your response as a JSON array of scenarios.
        """

        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in blockchain user experience design, specializing in creating intuitive interaction flows for smart contracts."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7  # Slightly higher temperature for creative scenarios
        )

        try:
            scenarios = json.loads(response.choices[0].message.content).get("scenarios", [])
            if not scenarios:
                # If the AI didn't use the expected format, try to parse the whole response
                scenarios = json.loads(response.choices[0].message.content)
            return scenarios
        except Exception as e:
            # Return a simple default scenario if parsing fails
            return [{
                "name": "Basic Interaction",
                "description": "User interacts with the main functions of the contract",
                "steps": [
                    "User connects wallet",
                    "User calls contract function",
                    "User receives confirmation"
                ]
            }]