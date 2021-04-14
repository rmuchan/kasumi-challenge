if __name__ == '__main__':
    import sys
    from ksm_challenge_src.version import log_file
    md_replace = {
        '\n': '  \n',
        '[': '\\[',
        ']': '\\]'
    }
    with open(sys.argv[1], 'w') as f:
        for item in log_file:
            f.write(f'### {item["version"]}\n')
            log = item['log']
            for k, v in md_replace.items():
                log = log.replace(k, v)
            f.write(log)
            f.write('\n\n')
    print(log_file[-1]['version'])
