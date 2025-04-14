def qlft_solution(aerosol_type='Saccharin', solution_type='Fit Test'):
    return f"""
    <tr>
        <td>
            <h4 style='padding-right: 1em'>{aerosol_type} {solution_type} Solution</h4>
        </td>
        <td>
            <h4>{aerosol_type} {solution_type} Solution</h4>
        </td>
    </tr>
    """

if __name__ == '__main__':
    amount = 8

    collection = ""
    for i in range(amount):
        collection += qlft_solution(aerosol_type='Saccharin', solution_type='Fit Test')
        collection += qlft_solution(aerosol_type='Saccharin', solution_type='Sensitivity')

    print(
    f"""
    <html>
        <body>
            <table>
                {collection}
            </table>
        </body>
    </html>
    """
    )

