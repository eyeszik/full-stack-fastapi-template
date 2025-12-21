"""Content template engine with variable substitution and formatting."""

import re
from typing import Any
from datetime import datetime
import uuid


class TemplateEngine:
    """Template engine for content with variable substitution.

    Supports:
    - Variable placeholders: {{variable_name}}
    - Conditional blocks: {{#if condition}}...{{/if}}
    - Loops: {{#each items}}...{{/each}}
    - Platform-specific variations
    - Built-in formatters: uppercase, lowercase, capitalize, truncate
    """

    VARIABLE_PATTERN = r'\{\{([^}]+)\}\}'
    IF_PATTERN = r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}'
    EACH_PATTERN = r'\{\{#each\s+(\w+)\}\}(.*?)\{\{/each\}\}'

    def __init__(self):
        """Initialize template engine."""
        self.formatters = {
            'uppercase': lambda x: str(x).upper(),
            'lowercase': lambda x: str(x).lower(),
            'capitalize': lambda x: str(x).capitalize(),
            'title': lambda x: str(x).title(),
            'truncate': lambda x, n=100: str(x)[:int(n)] + ('...' if len(str(x)) > int(n) else ''),
            'hashtag': lambda x: '#' + str(x).replace(' ', ''),
            'date': lambda x: datetime.fromisoformat(str(x)).strftime('%Y-%m-%d') if isinstance(x, (str, datetime)) else x,
            'time': lambda x: datetime.fromisoformat(str(x)).strftime('%H:%M') if isinstance(x, (str, datetime)) else x,
        }

    def render(
        self,
        template: str,
        variables: dict[str, Any],
        platform: str | None = None,
    ) -> str:
        """Render a template with variable substitution.

        Args:
            template: Template string with placeholders
            variables: Dictionary of variable values
            platform: Optional platform name for platform-specific templates

        Returns:
            Rendered string

        Examples:
            >>> engine = TemplateEngine()
            >>> engine.render("Hello {{name|uppercase}}", {"name": "John"})
            "Hello JOHN"

            >>> template = "Product: {{product}} - Price: ${{price}}"
            >>> engine.render(template, {"product": "Widget", "price": "99.99"})
            "Product: Widget - Price: $99.99"
        """
        result = template

        # Process platform-specific blocks first
        if platform:
            result = self._process_platform_blocks(result, platform)

        # Process loops
        result = self._process_loops(result, variables)

        # Process conditionals
        result = self._process_conditionals(result, variables)

        # Process variables
        result = self._process_variables(result, variables)

        return result.strip()

    def _process_variables(self, template: str, variables: dict[str, Any]) -> str:
        """Replace variable placeholders with values.

        Supports formatters: {{variable|formatter}}
        """
        def replace_variable(match):
            expression = match.group(1).strip()

            # Check for formatter pipe
            if '|' in expression:
                parts = expression.split('|')
                var_name = parts[0].strip()
                formatter_expr = parts[1].strip()

                # Parse formatter with optional arguments
                if '(' in formatter_expr:
                    formatter_name = formatter_expr[:formatter_expr.index('(')]
                    args_str = formatter_expr[formatter_expr.index('(') + 1:formatter_expr.rindex(')')]
                    args = [arg.strip().strip('"\'') for arg in args_str.split(',')]
                else:
                    formatter_name = formatter_expr
                    args = []

                value = variables.get(var_name, '')

                if formatter_name in self.formatters:
                    try:
                        return str(self.formatters[formatter_name](value, *args))
                    except Exception:
                        return str(value)

                return str(value)
            else:
                var_name = expression
                return str(variables.get(var_name, ''))

        return re.sub(self.VARIABLE_PATTERN, replace_variable, template)

    def _process_conditionals(self, template: str, variables: dict[str, Any]) -> str:
        """Process conditional blocks.

        {{#if variable}}content{{/if}}
        """
        def replace_conditional(match):
            condition = match.group(1).strip()
            content = match.group(2)

            # Check if condition is true
            if condition in variables and variables[condition]:
                return content
            return ''

        return re.sub(self.IF_PATTERN, replace_conditional, template, flags=re.DOTALL)

    def _process_loops(self, template: str, variables: dict[str, Any]) -> str:
        """Process loop blocks.

        {{#each items}}{{name}}{{/each}}
        """
        def replace_loop(match):
            collection_name = match.group(1).strip()
            loop_template = match.group(2)

            if collection_name not in variables:
                return ''

            collection = variables[collection_name]
            if not isinstance(collection, list):
                return ''

            results = []
            for item in collection:
                # If item is dict, make its keys available as variables
                if isinstance(item, dict):
                    loop_vars = {**variables, **item}
                else:
                    loop_vars = {**variables, 'item': item}

                results.append(self._process_variables(loop_template, loop_vars))

            return ''.join(results)

        return re.sub(self.EACH_PATTERN, replace_loop, template, flags=re.DOTALL)

    def _process_platform_blocks(self, template: str, platform: str) -> str:
        """Process platform-specific content blocks.

        {{#platform:youtube}}YouTube content{{/platform}}
        {{#platform:twitter}}Twitter content{{/platform}}
        """
        pattern = rf'\{{\{{#platform:(\w+)\}}(.*?)\{{/platform\}}'

        def replace_platform(match):
            block_platform = match.group(1).strip().lower()
            content = match.group(2)

            if block_platform == platform.lower():
                return content
            return ''

        return re.sub(pattern, replace_platform, template, flags=re.DOTALL)

    def extract_variables(self, template: str) -> list[str]:
        """Extract all variable names from a template.

        Args:
            template: Template string

        Returns:
            List of variable names

        Examples:
            >>> engine = TemplateEngine()
            >>> engine.extract_variables("Hello {{name}}, your {{item}} is ready")
            ['name', 'item']
        """
        variables = []
        matches = re.findall(self.VARIABLE_PATTERN, template)

        for match in matches:
            # Remove formatters
            if '|' in match:
                var_name = match.split('|')[0].strip()
            else:
                var_name = match.strip()

            # Skip special keywords
            if not var_name.startswith('#'):
                variables.append(var_name)

        return list(set(variables))

    def validate_template(self, template: str) -> tuple[bool, list[str]]:
        """Validate template syntax.

        Args:
            template: Template to validate

        Returns:
            Tuple of (is_valid, list of error messages)

        Examples:
            >>> engine = TemplateEngine()
            >>> valid, errors = engine.validate_template("Hello {{name}}")
            >>> valid
            True
        """
        errors = []

        # Check for unclosed tags
        open_ifs = template.count('{{#if')
        close_ifs = template.count('{{/if}}')
        if open_ifs != close_ifs:
            errors.append(f"Mismatched if tags: {open_ifs} open, {close_ifs} close")

        open_each = template.count('{{#each')
        close_each = template.count('{{/each}}')
        if open_each != close_each:
            errors.append(f"Mismatched each tags: {open_each} open, {close_each} close")

        open_platform = template.count('{{#platform:')
        close_platform = template.count('{{/platform}}')
        if open_platform != close_platform:
            errors.append(f"Mismatched platform tags: {open_platform} open, {close_platform} close")

        # Check for valid variable syntax
        variables = re.findall(r'\{\{([^}]*)\}\}', template)
        for var in variables:
            if not var.strip():
                errors.append("Empty variable placeholder found")

        return len(errors) == 0, errors


class PlatformContentFormatter:
    """Format content for specific social media platforms."""

    def __init__(self):
        """Initialize formatter."""
        self.template_engine = TemplateEngine()

    def format_for_platform(
        self,
        content: str,
        platform: str,
        options: dict[str, Any] | None = None,
    ) -> str:
        """Format content according to platform requirements.

        Args:
            content: Raw content text
            platform: Platform name (youtube, twitter, instagram, etc.)
            options: Platform-specific formatting options

        Returns:
            Formatted content
        """
        options = options or {}
        platform = platform.lower()

        if platform == 'twitter':
            return self._format_twitter(content, options)
        elif platform == 'instagram':
            return self._format_instagram(content, options)
        elif platform == 'youtube':
            return self._format_youtube(content, options)
        elif platform == 'facebook':
            return self._format_facebook(content, options)
        elif platform == 'linkedin':
            return self._format_linkedin(content, options)

        return content

    def _format_twitter(self, content: str, options: dict) -> str:
        """Format for Twitter (max 280 chars)."""
        max_length = options.get('max_length', 280)

        if len(content) > max_length:
            # Truncate with ellipsis
            content = content[:max_length - 3] + '...'

        # Add hashtags if provided
        if options.get('hashtags'):
            hashtags = ' '.join(f"#{tag.strip('#')}" for tag in options['hashtags'])
            available_space = max_length - len(content) - 1
            if len(hashtags) <= available_space:
                content = f"{content} {hashtags}"

        return content

    def _format_instagram(self, content: str, options: dict) -> str:
        """Format for Instagram (max 2200 chars)."""
        max_length = 2200

        if len(content) > max_length:
            content = content[:max_length]

        # Add hashtags at end if provided
        if options.get('hashtags'):
            hashtags = '\n\n' + ' '.join(f"#{tag.strip('#')}" for tag in options['hashtags'][:30])  # Max 30 hashtags
            if len(content) + len(hashtags) <= max_length:
                content += hashtags

        return content

    def _format_youtube(self, content: str, options: dict) -> str:
        """Format for YouTube description (max 5000 chars)."""
        max_length = 5000

        if len(content) > max_length:
            content = content[:max_length]

        # Add chapters if provided
        if options.get('chapters'):
            chapters_text = '\n\nChapters:\n' + '\n'.join(
                f"{chapter['time']} - {chapter['title']}"
                for chapter in options['chapters']
            )
            if len(content) + len(chapters_text) <= max_length:
                content += chapters_text

        return content

    def _format_facebook(self, content: str, options: dict) -> str:
        """Format for Facebook (max 63,206 chars)."""
        max_length = 63206

        if len(content) > max_length:
            content = content[:max_length]

        return content

    def _format_linkedin(self, content: str, options: dict) -> str:
        """Format for LinkedIn (max 3000 chars for posts)."""
        max_length = 3000

        if len(content) > max_length:
            content = content[:max_length]

        return content

    def generate_hashtags(
        self,
        content: str,
        count: int = 5,
        trending: list[str] | None = None,
    ) -> list[str]:
        """Generate relevant hashtags from content.

        Args:
            content: Content text
            count: Number of hashtags to generate
            trending: Optional list of trending hashtags to include

        Returns:
            List of hashtag strings
        """
        # Simple keyword extraction (in production, use NLP)
        words = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', content)

        # Add trending hashtags if provided
        hashtags = []
        if trending:
            hashtags.extend(trending[:count // 2])

        # Add content-based hashtags
        for word in words:
            if len(hashtags) >= count:
                break
            if len(word) > 3:  # Skip short words
                hashtag = word.replace(' ', '')
                if hashtag not in hashtags:
                    hashtags.append(hashtag)

        return hashtags[:count]
