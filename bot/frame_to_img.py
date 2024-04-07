from typing import List, Optional
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import six


def render_mpl_table(data: pd.DataFrame, col_width: float=3.0, row_height: float=0.625, font_size: float=14,
                     header_color: str='#40466e', row_colors: List[str]=['#f1f1f2', 'w'], edge_color: str='w',
                     bbox: List[int]=[0, 0, 1, 1], header_columns: float=0, file_path: Optional[str]=None,
                     fig=None, ax=None, **kwargs):
    """

    :param data:
    :param col_width:
    :param row_height:
    :param font_size:
    :param header_color:
    :param row_colors:
    :param edge_color:
    :param bbox:
    :param header_columns:
    :param file_path:
    :param ax:
    :param kwargs:
    :return:
    """
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)
    mpl_table.auto_set_column_width(col=list(range(len(data.columns))))
    mpl_table.auto_set_font_size(False)

    for k, cell in six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0] % len(row_colors)])

    if file_path: fig.savefig(file_path)

    return fig, ax