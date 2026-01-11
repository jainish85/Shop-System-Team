from django import template

register = template.Library()

@register.filter
def rupees(value):
    """
    Converts a number like 2540400 into 25,40,400.00
    Usage in HTML: {{ value|rupees }}
    """
    try:
        if value is None:
            return "0.00"
        
        # Convert to float to handle decimals, then to string
        value = float(value)
        s = "{:.2f}".format(value)
        parts = s.split('.')
        integer_part = parts[0]
        decimal_part = parts[1]
        
        if len(integer_part) <= 3:
            return s
            
        last_3 = integer_part[-3:]
        rest = integer_part[:-3]
        
        # Logic to split the rest into pairs of 2
        vals = []
        for i in range(len(rest) - 1, -1, -2):
            start = max(i - 1, 0)
            vals.append(rest[start:i+1])
        
        new_rest = ",".join(vals[::-1])
        return f"{new_rest},{last_3}.{decimal_part}"
        
    except (ValueError, TypeError):
        return value