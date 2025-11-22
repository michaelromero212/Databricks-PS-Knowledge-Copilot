class AnswerFormatter:
    @staticmethod
    def format(response: str) -> str:
        """Formats the LLM response (if needed)."""
        # The LLM is already instructed to format the output, so this might be a pass-through
        # or used for additional parsing if we want to separate Answer and Sources programmatically.
        return response
