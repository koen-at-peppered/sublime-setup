import sublime_plugin
import re


class VConvertCommand(sublime_plugin.WindowCommand):

    def is_enabled(self):
        view = self.window.active_view()
        if view.syntax().scope == 'source.scss':
            return True
        return False

    def run(self):
        view = self.window.active_view()
        content = []
        originals = []

        # collect original variable declarations
        with open(view.file_name()) as f:
            lines = f.readlines()
            for line in lines:
                match = re.match(r'^(\$[^:]+): (.*);$', line)
                if match:
                    originals.append((match.group(1), match.group(2)))

        f.close()

        # collect lines to be written out
        with open(view.file_name()) as f:
            lines = f.readlines()
            for line in lines:
                replaced = line
                for orig in originals:
                    escaped = '\\' + orig[0]
                    template = r'\1v({}, ~, {})'.format(orig[1], orig[0])
                    find = r'(^\s+([^:]+:\s*|@include fontsize\()){}'.format(escaped)
                    found = re.match(find, line)
                    if found:
                        intermediate = re.sub(find, template, line)

                        match = re.match(r'^\s+([^:]+):', intermediate)
                        if match:
                            prop = re.sub(r'-', '_', match.group(1))
                            replaced = re.sub(r'~', '~' + prop, intermediate)
                        else:
                            replaced = intermediate

                content.append(replaced)

        f.close()

        # write content back out
        with open(view.file_name(), 'w') as f:
            for line in content:
                f.write(line)

        f.close()
